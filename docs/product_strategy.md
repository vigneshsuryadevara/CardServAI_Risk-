# CardServ AI — Product Strategy

**Portfolio project | Synthetic data | Illustrative economics only**

## Executive decision

Build a controlled AI-assisted servicing experience for a narrow first-release scope: general explanations about interest, fees, payment due dates, and payment status. Keep account-specific decisions and sensitive workflows (fraud, lost/stolen cards, disputes, account changes) in authenticated servicing workflows until data access, controls, and operating procedures are approved.

## Customer problem

Cardholders may need repeated help understanding statement line items, due dates, fee triggers, or payment posting. Generic self-service experiences can fail when the answer needs explanation, relevant evidence, or clear next steps. This demo uses a synthetic contact dataset to illustrate how a business analyst could quantify the opportunity; it is not evidence about any real issuer's contact mix or performance.

## Product hypothesis

If a policy-grounded assistant provides concise explanations with visible sources and safe escalation, then selected low-risk contacts may be resolved with fewer transfers and repeat contacts—without increasing policy errors, customer complaints, or unsupported claims.

## Why start with these intents?

1. Use the contact dataset to rank volume, average handling time, repeat-contact rate, transfer rate, and risk.
2. Prioritize use cases with both measurable demand and a feasible approved-policy answer.
3. Exclude workflows requiring account changes, transaction adjudication, or urgent fraud actions from autonomous resolution.
4. Verify the choice with servicing operations, compliance, legal, product, data, and engineering before a pilot.

## MVP scope

- Answer general, non-account-specific questions from approved policy documents.
- Retrieve and cite the source snippets used.
- Clearly state when the answer depends on account-specific data.
- Recommend a human handoff when the customer asks for an account action or the issue is sensitive.
- Log intent, retrieved source IDs, confidence, escalation recommendation, latency, and outcome for evaluation.

## Out of scope

- Accessing real cardholder accounts or payment systems.
- Making payments, changing limits, reversing fees, or adjudicating disputes.
- Issuing guarantees about approval, refunds, posting times, or financial outcomes.
- Using these synthetic metrics as production claims.

## Success measures

**Primary business outcome:** cost per successfully resolved in-scope contact.

**Customer outcomes:** repeat-contact rate, CSAT, complaint rate, and abandonment.

**AI quality:** intent accuracy, retrieval hit rate, groundedness, completeness, escalation recall, unsupported-claim rate, and performance by intent/customer segment.

**Operational and risk guardrails:** policy-violation rate, privacy incidents, false containment, critical escalation misses, latency, cost per interaction, and drift.

## Pilot approach

1. Establish a baseline from approved historical contact and quality-assurance data.
2. Run offline evaluation on representative scenarios, including adversarial and edge cases.
3. Conduct a human-reviewed shadow period without changing the customer experience.
4. Run a small controlled pilot only after risk/legal/compliance and operations approval.
5. Expand by intent only when predefined quality and customer-outcome thresholds are met.

## Go / no-go decision

Go only if critical safety checks pass, target-intent performance beats the approved baseline, economics remain positive under conservative assumptions, and servicing operations can support escalation volume. Pause or roll back for critical policy errors, increased complaints, privacy incidents, or material drift.
