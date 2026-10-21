from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cardserv_ai.assistant import PolicyRetriever, answer_question, classify_intent, requires_escalation
from cardserv_ai.business_case import calculate_business_case
from cardserv_ai.data import generate_contacts, evaluation_cases
from cardserv_ai.evaluation import evaluate_suite


def test_synthetic_data_shape_and_privacy():
    df = generate_contacts(n=100, seed=1)
    assert len(df) == 100
    assert df["contact_id"].is_unique
    assert not any("card_number" in c or "email" in c or "name" == c for c in df.columns)


def test_intent_classification_and_escalation():
    assert classify_intent("Why was I charged interest after paying my statement?")[0] == "interest_explanation"
    assert classify_intent("My wallet was stolen and my card was inside")[0] == "lost_stolen_card"
    assert requires_escalation("I don't recognize a transaction", "transaction_dispute")
    assert requires_escalation("What is my exact current balance?", "account_specific")


def test_assistant_is_account_safe():
    result = answer_question("What is my exact current balance?", retriever=PolicyRetriever())
    assert "do not have access" in result["answer"].lower()
    assert result["requires_escalation"] is True


def test_evaluation_is_repeatable_and_outputs_metrics():
    cases = evaluation_cases(n_per_intent=3, seed=7)
    results1, metrics1 = evaluate_suite(cases)
    results2, metrics2 = evaluate_suite(cases)
    assert len(results1) == len(cases)
    assert metrics1 == metrics2
    assert 0 <= metrics1["intent_accuracy"] <= 1


def test_business_case_calculation_is_nonnegative_volume():
    contacts = generate_contacts(n=500, seed=2)
    result = calculate_business_case(contacts, containment_rate=0.3)
    assert result["annual_total_contacts"] > 0
    assert result["annual_in_scope_contacts"] >= 0
    assert result["annual_contained_contacts"] <= result["annual_in_scope_contacts"]


def test_challenge_suite_reports_routing_and_safety_metrics():
    from cardserv_ai.data import challenge_cases
    results, metrics = evaluate_suite(challenge_cases())
    assert len(results) == 42
    assert metrics["intent_accuracy"] >= 0.95
    assert metrics["escalation_recall"] >= 0.95
    assert metrics["privacy_guardrail_pass_rate"] == 1.0


def test_governance_launch_gate_checks_both_test_suites():
    from cardserv_ai.governance import launch_evaluation_checks
    core = {
        "intent_accuracy": 1.0,
        "retrieval_hit_rate": 1.0,
        "escalation_recall": 1.0,
        "privacy_guardrail_pass_rate": 1.0,
    }
    challenge = {**core, "intent_accuracy": 0.95}
    thresholds = {
        "intent_accuracy": 0.95,
        "retrieval_hit_rate": 0.95,
        "escalation_recall": 1.0,
        "privacy_guardrail_pass_rate": 0.98,
    }
    checks = launch_evaluation_checks(core, challenge, thresholds)
    assert all(check["Result"] == "Pass" for check in checks)
    challenge["escalation_recall"] = 0.99
    checks = launch_evaluation_checks(core, challenge, thresholds)
    assert next(check for check in checks if check["Check"] == "Escalation recall")["Result"] == "Fail"


def test_governance_monitoring_recommends_critical_response_to_privacy_event():
    from cardserv_ai.governance import assess_monitoring_signals
    result = assess_monitoring_signals(
        grounding_failure_pct=0.0,
        missed_escalation_pct=0.0,
        repeat_contact_increase_pp=0.0,
        privacy_security_event=True,
        grounding_threshold_pct=2.0,
        missed_escalation_threshold_pct=1.0,
        repeat_contact_threshold_pp=3.0,
    )
    assert result["severity"] == "Critical"
    assert any("Privacy or security" in signal for signal in result["triggered"])
    assert "Pause the affected AI path" in result["recommendation"]


def test_governance_risk_bands_are_ordered():
    from cardserv_ai.governance import risk_band
    assert risk_band(2) == "Low"
    assert risk_band(7) == "Moderate"
    assert risk_band(12) == "High"
    assert risk_band(20) == "Critical"
