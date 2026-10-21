from __future__ import annotations

import os
import re
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .data import load_knowledge_base

INTENTS = [
    "interest_explanation", "payment_due", "fee_explanation", "transaction_dispute",
    "payment_processing", "credit_limit", "lost_stolen_card", "fraud_suspicion", "account_specific",
]

KEYWORDS = {
    "lost_stolen_card": ["lost card", "lost my", "card is lost", "stolen card", "card missing", "card is missing", "my card is missing", "missing card", "wallet was stolen", "card was stolen", "someone stole my card", "can't find my credit card", "cannot find my credit card", "card is gone", "cancel my card", "lock my card", "replacement card", "my card is gone", "misplaced", "cannot locate it", "purse was taken", "card was taken", "taken from my bag", "card theft", "protect it"],
    "fraud_suspicion": ["fraud", "suspicious", "compromised", "compromise", "scammer", "someone is using", "unauthorized activity", "unknown purchase", "didn't make", "did not make", "card details", "account compromise", "cannot account for", "copied my payment details", "copied my card details", "payment details"],
    "transaction_dispute": ["don't recognize", "do not recognize", "dispute", "wrong transaction", "charged me twice", "incorrect transaction", "unauthorized charge", "wrong charge", "merchant charged", "report a card transaction", "transaction amount", "transaction i did not make", "purchase i did not make", "incorrect charge", "same amount twice", "cannot identify", "incorrect merchant amount", "purchase that wasn't mine", "purchase wasn't mine", "not mine", "duplicate merchant authorization", "duplicate merchant"],
    "interest_explanation": ["interest", "finance charge", "apr", "grace period"],
    "fee_explanation": ["fee", "late charge", "late-payment charge", "late-payment charges", "late payment charge", "annual charge", "service fee", "waiver", "refund this", "reverse my", "reverse the", "remove this charge", "adjustment"],
    "payment_processing": ["payment not showing", "not showing", "payment post", "payment posted", "posting", "pending payment", "payment status", "payment reflected", "not reflected", "confirm the payment", "made a payment", "payment went through", "did it go through", "payment still looks pending", "payment is pending", "payment was sent", "balance did not change", "recent payment", "payment isn't showing", "payment is not showing", "balance is unchanged", "amount due hasn't refreshed", "has not refreshed", "hasn't refreshed", "transfer left my account", "payment amount due"],
    "payment_due": ["minimum payment", "minimum due", "payment due", "due date", "amount do i need to pay", "amount i owe", "how much do i owe", "what amount do i pay", "deadline", "card bill", "minimum amount", "amount shown on the statement", "when should i pay"],
    "credit_limit": ["credit limit", "limit increase", "raise my limit", "more credit", "increase my limit", "limit review", "account change", "current limit", "check my limit", "higher credit", "higher credit limit", "credit line", "change my limit", "request a higher limit", "raise my card limit", "assistant raise my card limit", "spending limit", "more available credit", "larger card limit", "request more available credit", "higher credit line"],
    "account_specific": ["exact current balance", "current balance", "full card number", "make a payment", "make payment", "pay my bill", "my available credit", "my profile", "change my account", "human agent", "human representative", "current balance", "account balance"],
}

ESCALATION_KEYWORDS = [
    "reverse", "waive", "waiver", "refund", "adjustment", "dispute", "don't recognize", "do not recognize", "removed", "remove my fee", "remove the fee",
    "unauthorized", "stolen", "lost", "fraud", "suspicious", "not showing", "not posted", "not posting",
    "increase my limit", "raise my limit", "approve me", "exact current balance", "full card number",
    "make a payment", "make payment", "human agent", "human representative", "compromised", "payment status",
    "payment post", "payment posted", "payment not showing", "not reflected", "did it go through", "pending",
    "limit review", "higher credit limit", "credit limit increase", "change my credit limit", "limit increase", "current limit",
]


def classify_intent(question: str) -> tuple[str, float]:
    text = re.sub(r"\s+", " ", (question or "").lower()).strip()
    if not text:
        return "account_specific", 0.0
    scores = {}
    for intent, terms in KEYWORDS.items():
        score = 0.0
        for term in terms:
            if term in text:
                # A longer phrase is more discriminative than a generic token.
                score += 1.0 + min(len(term) / 30.0, 0.5)
        scores[intent] = score
    if max(scores.values(), default=0) <= 0:
        return "account_specific", 0.36
    # Prefer sensitive and specific intents over generic account requests if tied.
    priority = {name: i for i, name in enumerate([
        "lost_stolen_card", "fraud_suspicion", "transaction_dispute", "interest_explanation",
        "fee_explanation", "payment_processing", "payment_due", "credit_limit", "account_specific"
    ])}
    best = sorted(scores.items(), key=lambda p: (-p[1], priority.get(p[0], 99)))[0]
    positive = sum(v > 0 for v in scores.values())
    confidence = min(0.99, 0.68 + min(best[1], 2.0) * 0.12 - max(0, positive - 1) * 0.04)
    return best[0], round(max(0.4, confidence), 2)


def requires_escalation(question: str, intent: str | None = None) -> bool:
    text = (question or "").lower()
    intent = intent or classify_intent(text)[0]
    if intent in {"lost_stolen_card", "fraud_suspicion", "transaction_dispute", "account_specific", "payment_processing", "credit_limit"}:
        return True
    if intent == "fee_explanation" and any(term in text for term in ["reverse", "waive", "waiver", "refund", "adjust", "remove", "review a fee", "review this fee"]):
        return True
    return any(term in text for term in ESCALATION_KEYWORDS)


class PolicyRetriever:
    def __init__(self, documents: list[dict] | None = None):
        self.documents = documents or load_knowledge_base()
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([d["title"] + " " + d["content"] for d in self.documents])

    def retrieve(self, question: str, k: int = 3) -> list[dict[str, Any]]:
        qvec = self.vectorizer.transform([question or ""])
        scores = cosine_similarity(qvec, self.matrix).ravel()
        indices = np.argsort(scores)[::-1][:k]
        output = []
        for idx in indices:
            score = float(scores[int(idx)])
            if score < 0.001:
                continue
            doc = dict(self.documents[int(idx)])
            doc["score"] = round(score, 3)
            output.append(doc)
        return output


def _offline_response(question: str, intent: str, sources: list[dict]) -> str:
    text = (question or "").lower()
    templates = {
        "interest_explanation": (
            "Interest can still appear after a payment because the result depends on the card agreement, statement cycle, "
            "grace-period eligibility, balance type, and payment timing. Compare the interest line, statement balance, "
            "and payment date on your statement. I cannot determine your exact charge without verified account details. "
            "If those entries do not reconcile, ask servicing to review the account."
        ),
        "fee_explanation": (
            "Fee triggers and possible adjustments depend on the card agreement and account history. Review the fee line "
            "and the relevant agreement terms. I cannot confirm the reason for a specific fee or promise a waiver/refund "
            "from this demo; a fee reversal request needs an approved account-level review."
        ),
        "payment_due": (
            "Your statement and the issuer's authenticated app are the sources of truth for the minimum payment and due date. "
            "I do not have access to your account, so I cannot quote your personal amount or due date. Check the current "
            "statement or authenticated app before making a payment."
        ),
        "payment_processing": (
            "Payment posting can depend on the payment method, cut-off time, weekends, holidays, and issuer processing rules. "
            "I cannot verify whether your specific payment has posted. Check the authenticated app, and contact secure servicing "
            "if the payment is missing or the status appears incorrect."
        ),
        "transaction_dispute": (
            "For a transaction you do not recognize or believe is incorrect, use the issuer's official authenticated dispute "
            "or fraud-reporting channel promptly and keep relevant transaction details or receipts. I cannot remove a charge "
            "or determine the dispute outcome here. Do not share full card numbers, passwords, PINs, or one-time codes in chat."
        ),
        "lost_stolen_card": (
            "If your card is lost or stolen, use the issuer's official app or verified contact channel immediately to lock or "
            "report it. This demo cannot lock, cancel, or replace a card. Do not share your full card number, password, PIN, "
            "or one-time passcode here."
        ),
        "fraud_suspicion": (
            "Treat suspected unauthorized activity as time-sensitive. Use the issuer's official authenticated fraud-reporting "
            "channel immediately. I cannot verify transactions or secure the account from this demo. Never share passwords, PINs, "
            "full card numbers, or one-time codes in chat."
        ),
        "credit_limit": (
            "Credit-limit decisions and account changes depend on issuer rules and account-specific review. I cannot change your "
            "limit or predict an approval here. Use the authenticated app or the approved servicing workflow to request a review "
            "or check your current account-specific status."
        ),
        "account_specific": (
            "I do not have access to real card accounts and cannot retrieve balances, verify account status, make payments, or "
            "change account settings. Use the issuer's authenticated app or contact secure servicing for account-specific help. "
            "Please do not share card numbers, passwords, PINs, or one-time codes here."
        ),
    }
    answer = templates.get(intent, templates["account_specific"])
    if sources:
        citations = "; ".join(f"{doc['title']} ({doc['id']})" for doc in sources[:2])
        answer += f"\n\nSources: {citations}. These are illustrative sample documents, not official issuer policy."
    else:
        answer += "\n\nNo sufficiently relevant policy document was retrieved; use secure servicing for confirmation."
    if requires_escalation(question, intent):
        answer += "\n\nRecommended next step: route to an authenticated servicing workflow or qualified human specialist."
    return answer


def _openai_response(question: str, intent: str, sources: list[dict]) -> str:
    """Optional LLM synthesis; requires OPENAI_API_KEY and the openai package."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    source_text = "\n\n".join(f"[{d['id']}] {d['title']}\n{d['content']}" for d in sources)
    system = (
        "You are a conservative credit-card servicing assistant in a demo. Use only the supplied illustrative policy sources. "
        "Do not imply access to accounts or perform actions. Do not invent issuer rules, amounts, deadlines, approvals, or outcomes. "
        "If an account-specific request, fraud, lost/stolen card, dispute, or action request arises, tell the customer to use an "
        "official authenticated channel and recommend human review. Never request secrets. Explicitly state uncertainty. Cite source IDs. "
        "The sources are illustrative, not official issuer policy."
    )
    response = client.responses.create(
        model=model,
        input=[{"role": "system", "content": system},
               {"role": "user", "content": f"Intent: {intent}\nQuestion: {question}\n\nRetrieved sources:\n{source_text}"}],
        temperature=0.1,
    )
    return response.output_text.strip()


def answer_question(question: str, retriever: PolicyRetriever | None = None, use_openai: bool = False) -> dict:
    question = (question or "").strip()
    retriever = retriever or PolicyRetriever()
    intent, confidence = classify_intent(question)
    sources = retriever.retrieve(question, k=3) if question else []
    escalation = requires_escalation(question, intent)
    if not question:
        answer = "Enter a question to see a grounded sample response."
    elif use_openai and os.environ.get("OPENAI_API_KEY"):
        try:
            answer = _openai_response(question, intent, sources)
        except Exception as exc:
            answer = _offline_response(question, intent, sources)
            answer += f"\n\nLLM call unavailable; shown in safe offline mode ({type(exc).__name__})."
    else:
        answer = _offline_response(question, intent, sources)
    return {
        "question": question,
        "intent": intent,
        "intent_confidence": confidence,
        "requires_escalation": escalation,
        "answer": answer,
        "sources": sources,
        "mode": "OpenAI-assisted" if use_openai and os.environ.get("OPENAI_API_KEY") else "Offline safe demo",
    }
