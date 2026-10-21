"""Illustrative AI governance data and decision helpers for the CardServ AI demo."""
from __future__ import annotations

from typing import Any

USE_CASES: dict[str, dict[str, Any]] = {
    "policy_explanation": {
        "name": "Policy explanation assistant",
        "purpose": "Explain general fees, due dates, interest, and servicing policies using approved source material.",
        "business_owner": "Customer Servicing Product",
        "technical_owner": "AI Platform",
        "risk_tier": "Moderate",
        "data_class": "Public / illustrative policy text; no account data",
        "scope": "Answer general questions; no account actions or financial calculations",
        "version": "prompt-v0.4 · knowledge-base-v0.3",
        "why_risk": "An incorrect explanation could mislead a customer about fees, timing, or account terms.",
        "high_impact": False,
    },
    "payment_status": {
        "name": "Payment status and posting inquiries",
        "purpose": "Help authenticated customers understand the status of a specific payment.",
        "business_owner": "Servicing Operations",
        "technical_owner": "AI Platform",
        "risk_tier": "High",
        "data_class": "Potentially sensitive account and payment data",
        "scope": "Account-specific data access would require a separate authenticated integration; not implemented here",
        "version": "prompt-not-configured · integration-not-built",
        "why_risk": "A wrong or exposed payment status could create financial confusion or disclose account information.",
        "high_impact": True,
    },
    "dispute_guidance": {
        "name": "Transaction dispute guidance",
        "purpose": "Explain the dispute process and direct customers to the correct secure workflow.",
        "business_owner": "Disputes Product",
        "technical_owner": "AI Platform + Disputes Technology",
        "risk_tier": "High",
        "data_class": "Potentially sensitive transaction and account information",
        "scope": "Explain process only; do not determine dispute eligibility or outcome",
        "version": "prompt-not-configured · integration-not-built",
        "why_risk": "Misleading guidance could affect a customer's next steps, deadlines, or understanding of their rights.",
        "high_impact": True,
    },
}

COMMON_CONTROLS = [
    ("accountable_owner", "Business and technical owners are named", "Ownership"),
    ("policy_approval", "Policy source is approved and current", "Content and grounding"),
    ("privacy_review", "Data classification and privacy review are complete", "Privacy"),
    ("security_review", "Security and prompt-injection review are complete", "Security"),
    ("evaluation_review", "Offline evaluation has been reviewed against agreed thresholds", "Testing"),
    ("fallback_tested", "Human fallback and escalation paths have been tested", "Customer protection"),
    ("monitoring_defined", "Monitoring measures, thresholds, and accountable responders are defined", "Operations"),
    ("incident_runbook", "Incident response and rollback steps are documented", "Operations"),
    ("version_traceability", "Model, prompt, and knowledge-base versions are recorded", "Traceability"),
    ("formal_approval", "Required approvers and the decision path are identified", "Governance"),
]

HIGH_RISK_CONTROLS = [
    ("human_decision", "A qualified human retains consequential account or dispute decisions", "Human oversight"),
    ("auth_workflow", "Authentication, authorization, and least-privilege access are defined", "Access control"),
    ("red_team", "Adversarial, misuse, and sensitive-data tests have been reviewed", "Testing"),
    ("risk_acceptance", "Residual risk is accepted by the authorized risk owner and rationale is recorded", "Risk acceptance"),
]


def risk_band(score: float) -> str:
    """Return a simple illustrative score band; not a regulatory classification."""
    if score <= 4:
        return "Low"
    if score <= 9:
        return "Moderate"
    if score <= 15:
        return "High"
    return "Critical"


def launch_evaluation_checks(
    core: dict[str, float],
    challenge: dict[str, float],
    thresholds: dict[str, float],
) -> list[dict[str, Any]]:
    """Compare existing demo metrics with explicitly proposed launch thresholds."""
    metric_map = [
        ("Intent accuracy", "intent_accuracy", thresholds["intent_accuracy"]),
        ("Expected-source retrieval hit rate", "retrieval_hit_rate", thresholds["retrieval_hit_rate"]),
        ("Escalation recall", "escalation_recall", thresholds["escalation_recall"]),
        ("Privacy guardrail checks", "privacy_guardrail_pass_rate", thresholds["privacy_guardrail_pass_rate"]),
    ]
    checks = []
    for label, key, threshold in metric_map:
        core_val = float(core.get(key, 0.0))
        challenge_val = float(challenge.get(key, 0.0))
        passed = core_val >= threshold and challenge_val >= threshold
        checks.append({
            "Check": label,
            "Core suite": core_val,
            "Challenge suite": challenge_val,
            "Proposed minimum": threshold,
            "Result": "Pass" if passed else "Fail",
        })
    return checks


def assess_monitoring_signals(
    grounding_failure_pct: float,
    missed_escalation_pct: float,
    repeat_contact_increase_pp: float,
    privacy_security_event: bool,
    grounding_threshold_pct: float,
    missed_escalation_threshold_pct: float,
    repeat_contact_threshold_pp: float,
) -> dict[str, Any]:
    """Interpret user-entered simulated production signals for the demo."""
    triggered = []
    if grounding_failure_pct >= grounding_threshold_pct:
        triggered.append("Grounding failure rate at or above threshold")
    if missed_escalation_pct >= missed_escalation_threshold_pct:
        triggered.append("Missed-escalation rate at or above threshold")
    if repeat_contact_increase_pp >= repeat_contact_threshold_pp:
        triggered.append("Repeat-contact deterioration at or above threshold")
    if privacy_security_event:
        triggered.append("Privacy or security event reported")

    critical = privacy_security_event or missed_escalation_pct >= max(2 * missed_escalation_threshold_pct, 0.01)
    if critical:
        severity = "Critical"
        recommendation = (
            "Pause the affected AI path, route customers to the approved human workflow, preserve relevant evidence, "
            "notify the incident owner, and require investigation plus regression testing before reactivation."
        )
    elif triggered:
        severity = "High"
        recommendation = (
            "Pause expansion and consider restricting the affected intent. Review a representative sample, identify the "
            "cause, assign remediation, and rerun the relevant evaluation suite before scaling again."
        )
    else:
        severity = "No alert"
        recommendation = (
            "No configured threshold was breached in this simulation. Continue routine review; absence of an alert is not proof of safety."
        )
    return {"triggered": triggered, "severity": severity, "recommendation": recommendation}
