from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from cardserv_ai.assistant import PolicyRetriever, answer_question
from cardserv_ai.business_case import calculate_business_case, scenarios
from cardserv_ai.data import INTENT_TITLES, SAMPLE_PROMPTS, load_contacts, load_eval_cases, load_challenge_cases
from cardserv_ai.evaluation import baseline_metrics, evaluate_suite
from cardserv_ai.governance import (
    COMMON_CONTROLS, HIGH_RISK_CONTROLS, USE_CASES, assess_monitoring_signals,
    launch_evaluation_checks, risk_band,
)

st.set_page_config(page_title="CardServ AI | Servicing Intelligence", page_icon="◈", layout="wide")
st.markdown("""
<style>
:root { --ink:#15253D; --muted:#6D7A8D; --line:#E2E7EF; }
.block-container { padding-top: 1.3rem; padding-bottom: 2.5rem; max-width: 1440px; }
[data-testid="stSidebar"] { border-right: 1px solid #E2E7EF; }
.hero { padding: 1.4rem 1.6rem; border-radius: 18px; background: linear-gradient(115deg,#12233D 0%,#243F62 70%,#365E7F 100%); color: white; margin-bottom: 1.1rem; }
.hero .eyebrow { text-transform: uppercase; letter-spacing: .14em; font-size: .72rem; opacity: .78; font-weight: 700; }
.hero h1 { color: white; margin: .2rem 0 .35rem 0; font-size: 2rem; }
.hero p { color: #D7E4F2; margin: 0; max-width: 900px; }
.small-note { color: #6D7A8D; font-size: .83rem; }
.section-kicker { color: #58708A; text-transform: uppercase; letter-spacing: .11em; font-size: .72rem; font-weight: 800; margin-bottom: .15rem; }
div[data-testid="stMetric"] { background: #F7F9FC !important; border: 1px solid #E2E7EF; padding: 1rem 1rem .8rem 1rem; border-radius: 13px; }
/* Streamlit theme versions render metric labels through different nested elements.
   Force readable contrast on the label and every child, across all dashboard pages. */
div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricLabel"] p,
div[data-testid="stMetricLabel"] label { color: #52657D !important; opacity: 1 !important; }
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * { color: #15253D !important; opacity: 1 !important; }
[data-testid="stDataFrame"] { border: 1px solid #E2E7EF; border-radius: 10px; overflow: hidden; }
hr { border-color: #E2E7EF; }
</style>
""", unsafe_allow_html=True)

contacts = load_contacts()
eval_cases = load_eval_cases()
holdout_cases = load_challenge_cases()
retriever = PolicyRetriever()

with st.sidebar:
    st.markdown("## CardServ AI")
    st.caption("Servicing Intelligence & Optimization")
    page = st.radio("Workspace", ["Executive overview", "Contact analytics", "AI assistant", "Evaluation lab", "AI risk & governance", "Business case", "Product spec"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Demo status**")
    st.success("Synthetic data loaded", icon="✓")
    st.caption("No issuer systems or customer accounts are connected.")
    st.divider()
    st.caption("Independent portfolio prototype")


def hero(title: str, subtitle: str, tag: str = "PORTFOLIO DEMO"):
    st.markdown(f'<div class="hero"><div class="eyebrow">{tag}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def pct(v: float) -> str:
    return f"{v:.1%}"


def usd(v: float) -> str:
    return f"${v:,.0f}"


if page == "Executive overview":
    hero("Servicing intelligence and AI controls", "Use customer-contact analysis, policy retrieval, evaluation results, and economic assumptions to assess where assisted AI may be useful.")
    csat = contacts["csat_score"].mean()
    repeat_rate = contacts["repeat_contact_30d"].mean()
    transfer_rate = contacts["transferred"].mean()
    avg_aht = contacts["handle_time_minutes"].mean()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Synthetic contacts", f"{len(contacts):,}", help="Generated for this portfolio demo")
    c2.metric("Repeat contact", pct(repeat_rate))
    c3.metric("Transfer rate", pct(transfer_rate))
    c4.metric("Avg. handling time", f"{avg_aht:.1f} min")
    c5.metric("Avg. CSAT", f"{csat:.2f}/5")
    st.markdown("<div class='small-note'>All values above are computed from synthetic records and are not estimates of Capital One's actual performance.</div>", unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Where servicing demand concentrates")
        by_intent = contacts.groupby("intent_label", as_index=False).agg(Contacts=("contact_id", "count"), AHT=("handle_time_minutes", "mean"), Repeat=("repeat_contact_30d", "mean"))
        by_intent = by_intent.sort_values("Contacts", ascending=True)
        fig = px.bar(by_intent, x="Contacts", y="intent_label", orientation="h", text="Contacts", color="Contacts", color_continuous_scale=["#C9DAEA", "#315A7D"])
        fig.update_layout(height=390, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False, xaxis_title="Number of contacts", yaxis_title="")
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Outcome mix")
        outcome = contacts["outcome"].value_counts().rename_axis("Outcome").reset_index(name="Contacts")
        fig = px.pie(outcome, names="Outcome", values="Contacts", hole=0.62, color="Outcome", color_discrete_map={"Resolved":"#2D7A72", "Transferred":"#7897B8", "Unresolved":"#D58C54"})
        fig.update_layout(height=390, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h",y=-0.08))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Suggested product direction")
    a, b, c = st.columns(3)
    with a:
        st.markdown("**01 · Prioritize**")
        st.write("Start with high-volume intents where a clear policy explanation can help without taking account actions.")
    with b:
        st.markdown("**02 · Prove quality**")
        st.write("Use a labeled test set to check retrieval, intent routing, escalation, and privacy guardrails before launch.")
    with c:
        st.markdown("**03 · Prove value**")
        st.write("Compare conservative, base, and upside economics; pilot only when customer and risk metrics meet gates.")
    st.info("Decision principle: prioritize a measurable customer problem, not GenAI for its own sake.")

elif page == "Contact analytics":
    hero("Contact analytics", "Find the customer intents with the highest demand, handling burden, repeat contact, and transfer rates.", "DISCOVERY & PRIORITIZATION")
    intents = sorted(contacts["intent_label"].unique())
    channels = sorted(contacts["channel"].unique())
    f1, f2, f3 = st.columns([1.4,1,1])
    with f1:
        selected_intents = st.multiselect("Intents", intents, default=intents)
    with f2:
        selected_channels = st.multiselect("Channels", channels, default=channels)
    with f3:
        min_date = contacts["contact_date"].min().date()
        max_date = contacts["contact_date"].max().date()
        date_range = st.date_input("Contact dates", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    data = contacts[contacts["intent_label"].isin(selected_intents) & contacts["channel"].isin(selected_channels)].copy()
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        data = data[(data["contact_date"] >= start) & (data["contact_date"] <= end)]
    summary = data.groupby(["intent", "intent_label"], as_index=False).agg(
        Contacts=("contact_id", "count"), AHT_minutes=("handle_time_minutes", "mean"),
        Repeat_rate=("repeat_contact_30d", "mean"), Transfer_rate=("transferred", "mean"),
        Unresolved_rate=("outcome", lambda s: (s == "Unresolved").mean()), CSAT=("csat_score", "mean"),
    ).sort_values("Contacts", ascending=False)
    st.dataframe(summary.style.format({"AHT_minutes":"{:.1f}","Repeat_rate":"{:.1%}","Transfer_rate":"{:.1%}","Unresolved_rate":"{:.1%}","CSAT":"{:.2f}"}), use_container_width=True, hide_index=True)
    left, right = st.columns(2)
    with left:
        st.subheader("Repeat contact vs. handling time")
        fig = px.scatter(summary, x="AHT_minutes", y="Repeat_rate", size="Contacts", color="intent_label", hover_name="intent_label", labels={"AHT_minutes":"Avg. handling time (min)","Repeat_rate":"Repeat contact rate"})
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0), legend_title_text="Intent")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Transfers by intent")
        tdata = summary.sort_values("Transfer_rate")
        fig = px.bar(tdata, x="Transfer_rate", y="intent_label", orientation="h", color="Transfer_rate", color_continuous_scale=["#C9DAEA", "#315A7D"], labels={"Transfer_rate":"Transfer rate","intent_label":"Intent"})
        fig.update_xaxes(tickformat=".0%")
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    st.download_button("Download filtered analysis (CSV)", data.to_csv(index=False).encode("utf-8"), file_name="cardserv_filtered_contacts.csv", mime="text/csv")
    st.caption("Interpretation note: this is a generated dataset with deliberately varied intent-level outcomes. Replace with approved, de-identified data before making operational decisions.")

elif page == "AI assistant":
    hero("Policy-grounded AI assistant", "Ask a general card-servicing question. The demo retrieves sample policy text, drafts a cautious response, shows evidence, and flags when a secure human workflow is appropriate.", "WORKING PROTOTYPE")
    st.warning("Knowledge documents are fictional examples for product demonstration—not Capital One policy. The assistant has no account access and cannot perform transactions or account changes.")
    use_llm = False
    if os.environ.get("OPENAI_API_KEY"):
        use_llm = st.toggle("Use optional OpenAI response drafting", value=False, help="The app sends your entered question and retrieved sample-policy text to the configured OpenAI API. Do not enter personal or account data.")
    else:
        st.caption("Offline safe mode is active. To test optional LLM drafting, configure OPENAI_API_KEY locally using .env.example.")
    examples = st.selectbox("Try an example", ["Choose an example…"] + SAMPLE_PROMPTS)
    default_question = "" if examples == "Choose an example…" else examples
    question = st.text_area("Customer question", value=default_question, height=100, placeholder="For example: Why do I see interest after paying my statement?")
    if st.button("Generate response", type="primary"):
        if not question.strip():
            st.error("Enter a question first.")
        else:
            result = answer_question(question, retriever=retriever, use_openai=use_llm)
            st.session_state["last_answer"] = result
    result = st.session_state.get("last_answer")
    if result:
        st.divider()
        left, right = st.columns([1.5, 1])
        with left:
            st.subheader("Suggested response")
            st.write(result["answer"])
        with right:
            st.subheader("Routing signals")
            st.metric("Predicted intent", result["intent"].replace("_", " ").title())
            st.metric("Intent confidence", f"{result['intent_confidence']:.0%}")
            if result["requires_escalation"]:
                st.warning("Recommended: authenticated workflow / human review")
            else:
                st.success("No automatic escalation trigger detected; account-specific questions still require secure verification.")
            st.caption(f"Mode: {result['mode']}")
        st.subheader("Retrieved evidence")
        if result["sources"]:
            for doc in result["sources"]:
                with st.expander(f"{doc['title']} · {doc['id']} · relevance {doc['score']:.3f}"):
                    st.markdown(doc["content"])
        else:
            st.info("No sufficiently relevant knowledge-base document was retrieved. A production system should use a safe fallback rather than invent an answer.")
    st.caption("Prototype caveat: intent routing and offline answers use transparent heuristics. They are not a substitute for model evaluation, policy approval, or production controls.")

elif page == "Evaluation lab":
    hero("Evaluation lab", "Run the same test suite repeatedly, inspect failure patterns, and measure whether routing and retrieval meet proposed launch gates.", "QUALITY & RISK")
    st.warning("Results below are deterministic checks on a synthetic scenario set. They do not establish production accuracy, compliance, or safety.")
    if st.button("Run evaluation suite", type="primary") or "eval_results" not in st.session_state:
        results, metrics = evaluate_suite(eval_cases)
        holdout_results, holdout_metrics = evaluate_suite(holdout_cases)
        st.session_state["eval_results"] = results
        st.session_state["eval_metrics"] = metrics
        st.session_state["holdout_results"] = holdout_results
        st.session_state["holdout_metrics"] = holdout_metrics
    results = st.session_state["eval_results"]
    metrics = st.session_state["eval_metrics"]
    holdout_results = st.session_state["holdout_results"]
    holdout_metrics = st.session_state["holdout_metrics"]
    base = baseline_metrics(eval_cases)
    st.markdown("### Core regression suite")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Test cases", f"{metrics['n_cases']:,}")
    k2.metric("Intent accuracy", pct(metrics["intent_accuracy"]))
    k3.metric("Retrieval hit rate", pct(metrics["retrieval_hit_rate"]))
    k4.metric("Escalation recall", pct(metrics["escalation_recall"]))
    k5,k6,k7,k8 = st.columns(4)
    k5.metric("Escalation precision", pct(metrics["escalation_precision"]))
    k6.metric("Escalation decision accuracy", pct(metrics["escalation_accuracy"]))
    k7.metric("Citation rate", pct(metrics["citation_rate"]))
    k8.metric("Privacy guardrail checks", pct(metrics["privacy_guardrail_pass_rate"]))
    st.markdown("### Holdout challenge suite")
    h1,h2,h3,h4 = st.columns(4)
    h1.metric("Challenge cases", f"{holdout_metrics['n_cases']:,}")
    h2.metric("Intent accuracy", pct(holdout_metrics["intent_accuracy"]))
    h3.metric("Retrieval hit rate", pct(holdout_metrics["retrieval_hit_rate"]))
    h4.metric("Escalation recall", pct(holdout_metrics["escalation_recall"]))
    comp = pd.DataFrame([
        {"Metric":"Intent accuracy", "Core suite":metrics["intent_accuracy"], "Challenge suite":holdout_metrics["intent_accuracy"], "Generic human fallback":base["intent_accuracy"]},
        {"Metric":"Retrieval hit rate", "Core suite":metrics["retrieval_hit_rate"], "Challenge suite":holdout_metrics["retrieval_hit_rate"], "Generic human fallback":base["retrieval_hit_rate"]},
        {"Metric":"Escalation recall", "Core suite":metrics["escalation_recall"], "Challenge suite":holdout_metrics["escalation_recall"], "Generic human fallback":base["escalation_recall"]},
        {"Metric":"Citation rate", "Core suite":metrics["citation_rate"], "Challenge suite":holdout_metrics["citation_rate"], "Generic human fallback":base["citation_rate"]},
    ])
    st.subheader("Capability comparison")
    fig = px.bar(comp, x="Metric", y=["Core suite", "Challenge suite", "Generic human fallback"], barmode="group", range_y=[0,1], color_discrete_sequence=["#315A7D", "#D58C54", "#C0CCD9"])
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(height=360, margin=dict(l=0,r=0,t=10,b=0), legend_title_text="Approach")
    st.plotly_chart(fig, use_container_width=True)
    suite_choice = st.radio("Inspect results from", ["Challenge suite", "Core regression suite"], horizontal=True)
    inspect = holdout_results if suite_choice == "Challenge suite" else results
    filters = st.multiselect("Show case types", sorted(inspect["expected_intent"].unique()), default=sorted(inspect["expected_intent"].unique()), key="eval_intent_filters")
    # Evaluation outputs can contain missing flags for checks that do not apply to
    # a particular case. Normalize nullable values before applying boolean NOT.
    flag_columns = ["intent_correct", "retrieval_hit", "escalation_correct", "privacy_guardrail_pass"]
    for flag in flag_columns:
        inspect[flag] = inspect[flag].fillna(False).astype(bool)
    failed = inspect[
        inspect["expected_intent"].isin(filters)
        & (~inspect["intent_correct"] | ~inspect["retrieval_hit"] | ~inspect["escalation_correct"] | ~inspect["privacy_guardrail_pass"])
    ].copy()
    with st.expander(f"Inspect flagged cases ({len(failed)})", expanded=True):
        if len(failed):
            st.dataframe(failed[["case_id","question","expected_intent","predicted_intent","intent_correct","expected_source_id","retrieved_source_ids","retrieval_hit","expected_escalation","predicted_escalation","privacy_guardrail_pass"]], use_container_width=True, hide_index=True)
        else:
            st.write("No cases failed the current heuristic checks. This should not be interpreted as proof of production readiness.")
    st.subheader("Human review checklist")
    st.markdown("- Is the explanation factually correct and complete?\n- Is every material claim supported by approved policy?\n- Did the assistant avoid fabricated account details, deadlines, or promises?\n- Was escalation appropriate and timely?\n- Could the response confuse or disadvantage a vulnerable customer?")
    col_dl1, col_dl2 = st.columns(2)
    col_dl1.download_button("Download core results (CSV)", results.to_csv(index=False).encode("utf-8"), file_name="cardserv_core_evaluation_results.csv", mime="text/csv")
    col_dl2.download_button("Download challenge results (CSV)", holdout_results.to_csv(index=False).encode("utf-8"), file_name="cardserv_challenge_evaluation_results.csv", mime="text/csv")

elif page == "AI risk & governance":
    hero(
        "AI risk & governance",
        "Track use cases, test launch conditions, and rehearse the response to operational risk signals.",
        "RISK FRAMEWORK",
    )
    st.warning(
        "Portfolio simulation only. The inventory, owners, approvals, thresholds, and monitoring signals below are illustrative. "
        "They are not Capital One controls, formal compliance determinations, or live production telemetry."
    )

    # Calculate the same deterministic metrics used by the Evaluation Lab so the
    # launch gate is connected to existing project evidence rather than a static mock.
    @st.cache_data(show_spinner="Running the included test suites…")
    def _governance_eval_metrics():
        _, core_metrics = evaluate_suite(eval_cases)
        _, challenge_metrics = evaluate_suite(holdout_cases)
        return core_metrics, challenge_metrics

    core_metrics, challenge_metrics = _governance_eval_metrics()

    selected_case = st.selectbox(
        "Use case",
        options=list(USE_CASES),
        format_func=lambda key: USE_CASES[key]["name"],
        key="gov_selected_use_case",
    )
    case = USE_CASES[selected_case]
    st.markdown("### Use-case register")
    inventory_rows = []
    for key, item in USE_CASES.items():
        inventory_rows.append({
            "Use case": item["name"],
            "Inherent tier": item["risk_tier"],
            "Business owner": item["business_owner"],
            "Data class": item["data_class"],
            "Prototype status": "Working prototype" if key == "policy_explanation" else "Concept only",
            "Version / integration status": item["version"],
        })
    st.dataframe(pd.DataFrame(inventory_rows), use_container_width=True, hide_index=True)
    st.download_button(
        "Download use-case inventory (CSV)",
        pd.DataFrame(inventory_rows).to_csv(index=False).encode("utf-8"),
        file_name="cardserv_ai_use_case_inventory.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown(f"### Risk assessment · {case['name']}")
    st.write(case["purpose"])
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"**Business owner:** {case['business_owner']}")
        st.markdown(f"**Technical owner:** {case['technical_owner']}")
        st.markdown(f"**Data classification:** {case['data_class']}")
    with p2:
        st.markdown(f"**Current scope:** {case['scope']}")
        st.markdown(f"**Version traceability:** {case['version']}")
        st.markdown(f"**Primary risk:** {case['why_risk']}")

    r1, r2, r3 = st.columns(3)
    with r1:
        likelihood = st.slider("Likelihood (1 = rare, 5 = frequent)", 1, 5, 3, key=f"gov_likelihood_{selected_case}")
    with r2:
        impact = st.slider("Impact (1 = limited, 5 = severe)", 1, 5, 4 if case["high_impact"] else 3, key=f"gov_impact_{selected_case}")
    with r3:
        inherent_score = likelihood * impact
        st.metric("Inherent risk score", f"{inherent_score}/25", help="Likelihood × impact; an illustrative prioritization aid, not a compliance rating.")
        st.caption(f"Illustrative band: **{risk_band(inherent_score)}**")
    rr1, rr2, rr3 = st.columns(3)
    with rr1:
        residual_likelihood = st.slider("Residual likelihood after controls", 1, 5, max(1, likelihood - 1), key=f"gov_residual_likelihood_{selected_case}")
    with rr2:
        residual_impact = st.slider("Residual impact after controls", 1, 5, impact, key=f"gov_residual_impact_{selected_case}")
    with rr3:
        residual_score = residual_likelihood * residual_impact
        st.metric("Residual risk score", f"{residual_score}/25", delta=f"{residual_score - inherent_score:+d} vs. inherent", delta_color="inverse", help="Analyst-entered post-control estimate. It should be supported by evidence and independently reviewed.")
        st.caption(f"Illustrative band: **{risk_band(residual_score)}**")

    all_controls = COMMON_CONTROLS + (HIGH_RISK_CONTROLS if (case["high_impact"] or residual_score >= 10) else [])
    state_key = f"gov_controls_{selected_case}"
    if state_key not in st.session_state:
        # Seed the existing prototype with some evidence marked complete; all
        # remaining items need deliberate review in the interactive demo.
        seeded = {key: key in {"accountable_owner", "evaluation_review", "version_traceability"} for key, _, _ in all_controls}
        if selected_case == "policy_explanation":
            seeded.update({"fallback_tested": True})
        st.session_state[state_key] = seeded

    st.markdown("### Required controls")
    st.caption("Mark a control complete only when the supporting evidence has been reviewed. The default selections are illustrative, not evidence of actual approval.")
    controls = st.session_state[state_key]
    left, right = st.columns(2)
    for idx, (control_key, control_label, domain) in enumerate(all_controls):
        target = left if idx % 2 == 0 else right
        with target:
            controls[control_key] = st.checkbox(
                control_label,
                value=bool(controls.get(control_key, False)),
                key=f"gov_checkbox_{selected_case}_{control_key}",
                help=f"Control area: {domain}",
            )
    st.session_state[state_key] = controls

    st.markdown("### Proposed evaluation thresholds")
    st.caption("These are configurable demo gates. A real program should set thresholds by use case, severity, test coverage, and approved risk appetite.")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        min_intent = st.slider("Intent accuracy", 80, 100, 95, 1, format="%d%%", key="gov_min_intent") / 100
    with t2:
        min_retrieval = st.slider("Expected-source retrieval", 80, 100, 95, 1, format="%d%%", key="gov_min_retrieval") / 100
    with t3:
        min_escalation = st.slider("Escalation recall", 90, 100, 100, 1, format="%d%%", key="gov_min_escalation") / 100
    with t4:
        min_privacy = st.slider("Privacy checks", 90, 100, 98, 1, format="%d%%", key="gov_min_privacy") / 100
    thresholds = {
        "intent_accuracy": min_intent,
        "retrieval_hit_rate": min_retrieval,
        "escalation_recall": min_escalation,
        "privacy_guardrail_pass_rate": min_privacy,
    }
    eval_checks = launch_evaluation_checks(core_metrics, challenge_metrics, thresholds)
    eval_df = pd.DataFrame(eval_checks)
    eval_df["Core suite"] = eval_df["Core suite"].map(lambda x: f"{x:.1%}")
    eval_df["Challenge suite"] = eval_df["Challenge suite"].map(lambda x: f"{x:.1%}")
    eval_df["Proposed minimum"] = eval_df["Proposed minimum"].map(lambda x: f"{x:.1%}")
    st.dataframe(eval_df, use_container_width=True, hide_index=True)
    eval_gate_passed = all(row["Result"] == "Pass" for row in eval_checks)

    required_keys = {key for key, _, _ in all_controls}
    incomplete_controls = [label for key, label, _ in all_controls if not controls.get(key, False)]
    hard_gate_keys = {"accountable_owner", "policy_approval", "privacy_review", "security_review", "evaluation_review", "fallback_tested", "formal_approval"}
    if case["high_impact"] or residual_score >= 10:
        hard_gate_keys |= {"human_decision", "auth_workflow", "red_team", "risk_acceptance"}
    missing_hard_gates = [label for key, label, _ in all_controls if key in hard_gate_keys and not controls.get(key, False)]
    if missing_hard_gates or not eval_gate_passed:
        gate_status = "Blocked"
        gate_detail = "One or more critical controls or proposed evaluation thresholds are unmet. Do not progress to pilot review until gaps are resolved."
    elif incomplete_controls:
        gate_status = "Gaps remain"
        gate_detail = "Critical checks pass, but one or more operational controls are incomplete. Close the gaps before a launch decision."
    else:
        gate_status = "Ready for accountable review"
        gate_detail = "The configured checks pass. This means ready for a documented human decision—not automatic authorization to launch."

    st.markdown("### Launch decision")
    gate_col, evidence_col = st.columns([1, 1.6])
    with gate_col:
        if gate_status == "Blocked":
            st.error(f"**{gate_status}**\n\n{gate_detail}")
        elif gate_status == "Gaps remain":
            st.warning(f"**{gate_status}**\n\n{gate_detail}")
        else:
            st.success(f"**{gate_status}**\n\n{gate_detail}")
        st.metric("Incomplete controls", len(incomplete_controls))
    with evidence_col:
        if incomplete_controls:
            st.markdown("**Open items**")
            st.write("\n".join([f"- {item}" for item in incomplete_controls]))
        if not eval_gate_passed:
            st.markdown("**Evaluation gate failures**")
            st.write(", ".join(row["Check"] for row in eval_checks if row["Result"] != "Pass"))
        if gate_status == "Ready for accountable review":
            st.info("Review should include named business, technology, risk, compliance, and operations owners as applicable to the use case.")

    decision_key = f"gov_decision_{selected_case}"
    decision = st.selectbox(
        "Record a simulated review outcome",
        ["Not recorded", "Approve controlled pilot (demo)", "Hold / remediate"],
        key=decision_key,
        help="This records a decision in this browser session only. It does not approve a real release.",
    )
    if decision == "Approve controlled pilot (demo)" and gate_status != "Ready for accountable review":
        st.error("Approval cannot be recorded in this simulation while the configured launch gate is not ready for review.")
    elif decision == "Approve controlled pilot (demo)":
        st.success("Simulated decision recorded: controlled pilot approved, subject to the stated scope and operating limits.")
    elif decision == "Hold / remediate":
        st.warning("Simulated decision recorded: hold and assign remediation before reassessment.")

    snapshot = {
        "use_case_id": selected_case,
        "use_case": case["name"],
        "inherent_likelihood": likelihood,
        "inherent_impact": impact,
        "inherent_score": inherent_score,
        "risk_band": risk_band(inherent_score),
        "residual_likelihood": residual_likelihood,
        "residual_impact": residual_impact,
        "residual_score": residual_score,
        "residual_risk_band": risk_band(residual_score),
        "controls": {key: bool(controls.get(key, False)) for key in required_keys},
        "incomplete_controls": incomplete_controls,
        "evaluation_thresholds": thresholds,
        "evaluation_checks": eval_checks,
        "evaluation_gate_passed": eval_gate_passed,
        "launch_gate_status": gate_status,
        "simulated_review_outcome": decision,
        "note": "Illustrative portfolio assessment. Not a formal risk assessment, compliance approval, or production control record.",
    }
    st.download_button(
        "Download current assessment (JSON)",
        data=__import__("json").dumps(snapshot, indent=2).encode("utf-8"),
        file_name=f"cardserv_risk_assessment_{selected_case}.json",
        mime="application/json",
    )

    st.divider()
    st.markdown("### Post-launch monitoring rehearsal")
    st.caption("Enter hypothetical monitoring values to test the response process. These are not live production metrics.")
    m1, m2, m3 = st.columns(3)
    with m1:
        grounding_failure = st.slider("Responses with grounding failure (%)", 0.0, 10.0, 1.0, 0.5, key="gov_grounding_failure")
    with m2:
        missed_escalation = st.slider("Missed-escalation rate (%)", 0.0, 10.0, 0.0, 0.5, key="gov_missed_escalation")
    with m3:
        repeat_increase = st.slider("Repeat-contact increase (percentage points)", 0.0, 15.0, 0.0, 0.5, key="gov_repeat_increase")
    mon1, mon2, mon3, mon4 = st.columns(4)
    with mon1:
        grounding_threshold = st.number_input("Grounding alert threshold (%)", 0.5, 10.0, 2.0, 0.5, key="gov_grounding_threshold")
    with mon2:
        escalation_threshold = st.number_input("Missed-escalation threshold (%)", 0.5, 5.0, 1.0, 0.5, key="gov_escalation_threshold")
    with mon3:
        repeat_threshold = st.number_input("Repeat-contact alert (pp)", 0.5, 15.0, 3.0, 0.5, key="gov_repeat_threshold")
    with mon4:
        privacy_event = st.checkbox("Privacy / security event reported", key="gov_privacy_event")

    monitor = assess_monitoring_signals(
        grounding_failure_pct=grounding_failure,
        missed_escalation_pct=missed_escalation,
        repeat_contact_increase_pp=repeat_increase,
        privacy_security_event=privacy_event,
        grounding_threshold_pct=grounding_threshold,
        missed_escalation_threshold_pct=escalation_threshold,
        repeat_contact_threshold_pp=repeat_threshold,
    )
    if monitor["severity"] == "Critical":
        st.error(f"**{monitor['severity']} signal**\n\n{monitor['recommendation']}")
    elif monitor["severity"] == "High":
        st.warning(f"**{monitor['severity']} signal**\n\n{monitor['recommendation']}")
    else:
        st.info(f"**{monitor['severity']}**\n\n{monitor['recommendation']}")
    if monitor["triggered"]:
        st.markdown("**Triggered signals**")
        st.write("\n".join([f"- {signal}" for signal in monitor["triggered"]]))

    st.markdown("#### Incident log")
    with st.form("gov_incident_form", clear_on_submit=True):
        inc1, inc2 = st.columns([1, 2])
        with inc1:
            incident_severity = st.selectbox("Incident severity", ["Low", "Moderate", "High", "Critical"], index=2)
            incident_owner = st.text_input("Accountable incident owner", value=case["business_owner"])
        with inc2:
            incident_summary = st.text_input("Incident summary", placeholder="e.g., fee explanation returned an outdated policy source")
            incident_action = st.text_input("Immediate containment / next action", placeholder="e.g., route affected questions to a human and review source versions")
        incident_submitted = st.form_submit_button("Record sample incident")
    if incident_submitted:
        if not incident_summary.strip() or not incident_owner.strip():
            st.error("Enter an incident summary and an accountable owner.")
        else:
            from datetime import datetime, timezone
            entry = {
                "Recorded (UTC)": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "Use case": case["name"],
                "Severity": incident_severity,
                "Summary": incident_summary.strip(),
                "Owner": incident_owner.strip(),
                "Containment / next action": incident_action.strip(),
                "Record type": "Sample portfolio incident",
            }
            st.session_state.setdefault("gov_incidents", []).insert(0, entry)
            st.success("Sample incident recorded in this browser session.")
    incidents = st.session_state.get("gov_incidents", [])
    if incidents:
        incident_df = pd.DataFrame(incidents)
        st.dataframe(incident_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download incident log (CSV)",
            incident_df.to_csv(index=False).encode("utf-8"),
            file_name="cardserv_ai_sample_incident_log.csv",
            mime="text/csv",
        )
    else:
        st.caption("No incidents recorded in this session. Session entries are not a persistent audit log; a production implementation needs approved durable storage and access controls.")

    st.markdown("### Operating principles")
    principles = pd.DataFrame([
        {"Principle": "Risk-based scope", "Application": "Start with policy explanations; treat account-specific, payment, and dispute workflows as higher-risk scope requiring more evidence."},
        {"Principle": "Evidence before release", "Application": "Use test results and completed controls as inputs to human review; a score alone cannot authorize deployment."},
        {"Principle": "Traceability", "Application": "Record the use case, policy source, prompt/model version, evaluation evidence, decision, and remediation."},
        {"Principle": "Human fallback", "Application": "Keep a controlled human path for unsupported, sensitive, ambiguous, or consequential customer requests."},
        {"Principle": "Monitor and respond", "Application": "Define thresholds, owners, incident procedures, restrictions, retesting, and explicit reactivation criteria before scale-up."},
    ])
    st.dataframe(principles, use_container_width=True, hide_index=True)
    st.caption("The framework is a portfolio design proposal. Any production use would need to align with the organization's approved model-risk, information-security, privacy, compliance, and operational-risk processes.")

elif page == "Business case":
    hero("Business case & scenario planning", "Translate contact volume and a containment hypothesis into labor value, AI operating cost, and a Year 1 investment view.", "ILLUSTRATIVE ECONOMICS")
    st.warning("These are scenario assumptions applied to synthetic contact records—not actual Capital One volumes, costs, savings, or approved financial forecasts.")
    all_intents = sorted(contacts["intent"].unique())
    default_intents = ["interest_explanation", "payment_due", "fee_explanation", "payment_processing", "credit_limit"]
    selected = st.multiselect("In-scope first-release intents", all_intents, default=default_intents, format_func=lambda x: INTENT_TITLES.get(x,x))
    c1,c2,c3 = st.columns(3)
    with c1:
        annual_volume = st.number_input("Projected annual servicing contacts", min_value=1000, max_value=100000000, value=250000, step=25000, help="Planning assumption, not inferred from the 5,000-row synthetic sample. Replace with validated business volume.")
        contain = st.slider("Target containment rate", 0, 70, 30, 5, format="%d%%") / 100
        labor = st.slider("Loaded labor cost per hour", 15, 65, 34, 1, format="$%d")
    with c2:
        ai_cost = st.slider("AI cost per in-scope interaction", 0.01, 0.50, 0.10, 0.01, format="$%.2f")
        platform = st.number_input("Annual platform / operations cost ($)", 0, 500000, 50000, 5000)
    with c3:
        build = st.number_input("One-time build / integration cost ($)", 0, 1000000, 80000, 10000)
        months = st.slider("Implementation duration (months)", 1, 18, 6)
    model = calculate_business_case(contacts, target_intents=selected, containment_rate=contain, loaded_hourly_cost=labor, ai_cost_per_interaction=ai_cost, annual_platform_cost=platform, one_time_build_cost=build, implementation_months=months, annual_contact_volume=annual_volume)
    x1,x2,x3,x4 = st.columns(4)
    x1.metric("Annual in-scope contacts", f"{model['annual_in_scope_contacts']:,.0f}")
    x2.metric("Annual contained contacts", f"{model['annual_contained_contacts']:,.0f}")
    x3.metric("Steady-state net benefit", usd(model["steady_state_net_benefit"]))
    x4.metric("Year 1 net benefit", usd(model["year1_net_benefit"]))
    chart = pd.DataFrame({"Cost / value":["Gross labor savings","AI variable cost","Platform / operations","One-time build"], "Amount":[model["gross_labor_savings"],-model["ai_variable_cost"],-model["annual_platform_cost"],-model["one_time_build_cost"]]})
    fig = px.bar(chart, x="Cost / value", y="Amount", color="Amount", color_continuous_scale=["#C36C56","#D8E2EB","#2D7A72"])
    fig.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False, yaxis_title="Annualized USD (Year 1 includes build cost)")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Scenario comparison")
    scenario_df = scenarios(contacts, annual_contact_volume=annual_volume, target_intents=selected)
    st.dataframe(scenario_df.style.format({"Containment rate":"{:.0%}","Annual in-scope contacts":"{:,.0f}","Gross labor savings":"${:,.0f}","Annual AI + platform cost":"${:,.0f}","Steady-state net benefit":"${:,.0f}","Year 1 net benefit":"${:,.0f}"}), use_container_width=True, hide_index=True)
    if model["break_even_months"] is not None:
        st.metric("Simple payback after steady-state economics begin", f"{model['break_even_months']:.1f} months", help="One-time build cost divided by positive steady-state monthly net benefit; ignores implementation ramp and discounting.")
    else:
        st.error("No break-even under the selected assumptions. Consider a narrower scope, lower cost, better evidence, or do not proceed.")
    st.caption("This model excludes discounting, staffing constraints, implementation ramp effects, false-containment costs, customer lifetime value, and other costs not provided in the inputs.")

else:
    hero("Product strategy & launch controls", "The project artifacts that connect analytics, requirements, evaluation, and funding decisions.", "PRODUCT STRATEGY")
    tabs = st.tabs(["Strategy", "Requirements", "Evaluation plan", "Business case assumptions", "Risk framework"])
    docs = {
        "Strategy": ROOT / "docs" / "product_strategy.md",
        "Requirements": ROOT / "docs" / "product_requirements.md",
        "Evaluation plan": ROOT / "docs" / "evaluation_plan.md",
        "Business case assumptions": ROOT / "docs" / "business_case.md",
        "Risk framework": ROOT / "docs" / "risk_framework.md",
    }
    for tab, (name, path) in zip(tabs, docs.items()):
        with tab:
            st.markdown(path.read_text(encoding="utf-8"))
    st.download_button("Download project strategy", (ROOT / "docs" / "product_strategy.md").read_bytes(), file_name="product_strategy.md", mime="text/markdown")

st.divider()
st.caption("CardServ AI is an independent portfolio concept using synthetic data and illustrative sample policies. It is not affiliated with or endorsed by Capital One.")
