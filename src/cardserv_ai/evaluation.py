from __future__ import annotations
import re
import pandas as pd
from .assistant import PolicyRetriever, answer_question, classify_intent, requires_escalation
from .data import load_eval_cases


def evaluate_suite(cases: pd.DataFrame | None = None) -> tuple[pd.DataFrame, dict]:
    cases = cases if cases is not None else load_eval_cases()
    retriever = PolicyRetriever()
    results = []
    for row in cases.to_dict(orient="records"):
        result = answer_question(row["question"], retriever=retriever, use_openai=False)
        sources = result["sources"]
        expected_source = row.get("expected_source_id")
        has_expected_source = pd.notna(expected_source) and str(expected_source).strip() not in {"", "nan", "None"}
        source_hit = any(s["id"] == expected_source for s in sources) if has_expected_source else None
        expected_escalation = str(row.get("expected_escalation", False)).lower() in {"true", "1", "yes"}
        text = result["answer"].lower()
        privacy_guardrail = True
        if result["intent"] == "account_specific":
            privacy_guardrail = ("do not have access" in text or "cannot retrieve" in text or "cannot" in text)
        if result["intent"] in {"lost_stolen_card", "fraud_suspicion", "transaction_dispute"}:
            privacy_guardrail = privacy_guardrail and ("official" in text or "authenticated" in text)
        results.append({
            **row,
            "predicted_intent": result["intent"],
            "intent_correct": result["intent"] == row["expected_intent"],
            "retrieval_hit": source_hit,
            "predicted_escalation": result["requires_escalation"],
            "expected_escalation_bool": expected_escalation,
            "escalation_correct": result["requires_escalation"] == expected_escalation,
            "citation_present": "sources:" in text,
            "privacy_guardrail_pass": privacy_guardrail,
            "response_preview": result["answer"][:500],
            "retrieved_source_ids": ", ".join(s["id"] for s in sources),
        })
    df = pd.DataFrame(results)
    tp = int(((df["predicted_escalation"]) & (df["expected_escalation_bool"])).sum())
    fp = int(((df["predicted_escalation"]) & (~df["expected_escalation_bool"])).sum())
    fn = int(((~df["predicted_escalation"]) & (df["expected_escalation_bool"])).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    metrics = {
        "n_cases": int(len(df)),
        "intent_accuracy": float(df["intent_correct"].mean()) if len(df) else 0.0,
        "retrieval_hit_rate": float(df.loc[df["expected_source_id"].notna() & (df["expected_source_id"] != ""), "retrieval_hit"].mean()),
        "escalation_precision": float(precision),
        "escalation_recall": float(recall),
        "escalation_accuracy": float(df["escalation_correct"].mean()) if len(df) else 0.0,
        "citation_rate": float(df["citation_present"].mean()) if len(df) else 0.0,
        "privacy_guardrail_pass_rate": float(df["privacy_guardrail_pass"].mean()) if len(df) else 0.0,
    }
    return df, metrics


def baseline_metrics(cases: pd.DataFrame | None = None) -> dict:
    """A simple, intentionally weak FAQ baseline used only for comparison in the demo."""
    cases = cases if cases is not None else load_eval_cases()
    # Baseline sends generic traffic to a human; no retrieval or intent routing.
    return {
        "n_cases": int(len(cases)),
        "intent_accuracy": 0.0,
        "retrieval_hit_rate": 0.0,
        "escalation_precision": float(cases["expected_escalation"].astype(str).str.lower().isin(["true", "1", "yes"]).mean()),
        "escalation_recall": 1.0,
        "escalation_accuracy": float(cases["expected_escalation"].astype(str).str.lower().isin(["true", "1", "yes"]).mean()),
        "citation_rate": 0.0,
        "privacy_guardrail_pass_rate": 1.0,
    }
