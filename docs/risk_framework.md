# AI Risk Framework — CardServ AI

## Purpose

This framework is a proposed operating model for the portfolio prototype. It demonstrates how a servicing AI use case could be inventoried, assessed, tested, reviewed, monitored, and restricted when needed. It is not Capital One policy, a regulatory interpretation, or a substitute for an organization's approved control framework.

## 1. Inventory and accountability

Every use case should have a named business owner and technical owner, a defined customer problem and scope, intended users, data classification, model/prompt/knowledge-source versions, lifecycle status, and a documented human fallback. The register distinguishes the policy-explanation prototype from concepts that would need separate authenticated integrations.

## 2. Risk assessment

Assess inherent likelihood and impact, with rationale for each rating. Assess residual likelihood and impact after controls, supported by evidence rather than assuming that the existence of a control makes risk disappear. A simple 1–5 likelihood × 1–5 impact score is used in this demo only to support prioritization; it is not a formal risk classification.

Consider at least:

- Customer harm from incorrect, incomplete, or misleading explanations.
- Privacy exposure, unauthorized disclosure, and security misuse.
- Unsupported answers, retrieval failure, stale policy, and prompt injection.
- Incorrect or missed escalation and the availability of human support.
- Fairness, accessibility, customer vulnerability, complaint, and repeat-contact outcomes.
- Vendor/model changes, operational resilience, latency, cost, and traceability.

## 3. Proposed launch gate

Before a pilot is considered, the team should have evidence that:

1. The scope and accountable owners are clear.
2. Policy sources are approved and current, and data use has been reviewed.
3. Security, privacy, and relevant compliance reviews are complete.
4. Offline tests cover expected behavior, weak/irrelevant retrieval, sensitive requests, escalation, prompt injection, and likely failure modes.
5. Evaluation thresholds are agreed for the use case and reviewed alongside qualitative human assessment.
6. A human fallback, incident owner, monitoring plan, and rollback path have been tested.
7. Required approvers have reviewed the evidence and recorded a decision.

Passing a numeric test threshold is necessary only where applicable; it is never sufficient by itself to authorize release. High-impact or account-specific use cases need stronger evidence and controls than general policy explanations.

## 4. Monitoring and response

A production design should monitor source-grounding failures, answer quality from human review, missed and unnecessary escalations, repeat contacts, confirmed resolution, complaints, privacy/security events, drift, latency, and cost. Segment results by use case, intent, policy version, model/prompt version, channel, and other permitted dimensions.

| Signal | Illustrative response |
|---|---|
| Privacy or security event | Restrict or disable the affected path, route to the approved human workflow, preserve evidence, and notify accountable responders. |
| Missed escalation or severe answer defect | Pause expansion; restrict the affected intent; investigate, remediate, and rerun relevant tests before reactivation. |
| Grounding, repeat-contact, or complaint deterioration | Review samples, determine cause, assign remediation, and assess customer impact before scaling. |
| New intent, policy update, or model/prompt change | Version the change, run regression and challenge tests, and obtain the required review before release. |

Thresholds must be set by the responsible team based on intended use, severity, customer impact, observed baseline, test power, and risk appetite. The threshold values in the app are editable examples, not recommended bank standards.

## 5. Incident record

Each incident record should capture timestamp, affected use case and version, severity, customer impact where known, detection source, owner, containment, root cause, corrective action, retest evidence, and the person authorized to approve reactivation. A production system should store these records in approved durable storage with appropriate access control and audit history.

## 6. Limits of this prototype

- The data, use-case owners, controls, review outcomes, thresholds, and monitoring signals are sample values.
- Evaluation results are generated from hand-authored synthetic cases and simple heuristic checks.
- The current app does not connect to production telemetry, customer accounts, formal approval services, or a durable incident-management system.
- Session-created incidents and decisions are not a persistent audit record.
- A completed checklist is not proof of regulatory compliance or production readiness.
