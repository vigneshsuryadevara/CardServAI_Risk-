from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pandas as pd
from cardserv_ai.business_case import scenarios
from cardserv_ai.data import load_challenge_cases, load_contacts, load_eval_cases
from cardserv_ai.evaluation import evaluate_suite


def print_metrics(name, metrics):
    print(f"\n{name} — deterministic heuristic checks")
    for key, value in metrics.items():
        if key == "n_cases":
            print(f"{key:30s}: {value}")
        else:
            print(f"{key:30s}: {value:.1%}")


def main():
    contacts = load_contacts(ROOT / "data" / "synthetic_contacts.csv")
    core_results, core_metrics = evaluate_suite(load_eval_cases(ROOT / "data" / "evaluation_cases.csv"))
    challenge_results, challenge_metrics = evaluate_suite(load_challenge_cases(ROOT / "data" / "challenge_cases.csv"))
    print_metrics("Core regression suite", core_metrics)
    print_metrics("Challenge suite", challenge_metrics)
    out = ROOT / "artifacts"
    out.mkdir(exist_ok=True)
    core_results.to_csv(out / "core_evaluation_results.csv", index=False)
    challenge_results.to_csv(out / "challenge_evaluation_results.csv", index=False)
    summary = {
        "core_regression_suite": core_metrics,
        "challenge_suite": challenge_metrics,
        "interpretation": "Deterministic heuristic checks against synthetic labels; not a model benchmark or evidence of production readiness.",
    }
    (out / "evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    contact_summary = contacts.groupby(["intent", "intent_label"], as_index=False).agg(
        contacts=("contact_id", "count"), mean_handle_time_minutes=("handle_time_minutes", "mean"),
        repeat_contact_rate=("repeat_contact_30d", "mean"), transfer_rate=("transferred", "mean"),
        unresolved_rate=("outcome", lambda s: (s == "Unresolved").mean()), mean_csat=("csat_score", "mean"),
    ).sort_values("contacts", ascending=False)
    contact_summary.to_csv(out / "contact_analytics_summary.csv", index=False)
    scenarios(contacts, annual_contact_volume=250000).to_csv(out / "business_case_scenarios.csv", index=False)
    print(f"\nArtifacts written to {out}")


if __name__ == "__main__":
    main()
