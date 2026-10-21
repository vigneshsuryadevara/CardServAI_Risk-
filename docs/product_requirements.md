# Product Requirements — CardServ AI

## User story

As a cardholder, I want a clear explanation of a general card-servicing question, with supporting policy evidence and a safe next step, so that I can understand what to do without repeating the same contact.

## Functional requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-01 | Intent classification | Every interaction receives an intent label and confidence value; unknown or conflicting requests default to a safe path. |
| FR-02 | Policy retrieval | The assistant retrieves relevant approved content; source IDs and relevance scores are logged. |
| FR-03 | Grounded answer | The answer uses retrieved content, identifies uncertainty, and does not invent account-specific amounts, decisions, deadlines, or promises. |
| FR-04 | Human escalation | Fraud, lost/stolen cards, disputed transactions, account-specific requests, and action requests route to a secure approved workflow. |
| FR-05 | Privacy protection | The assistant does not request or expose full card numbers, passwords, PINs, or one-time codes. |
| FR-06 | Evaluation | Every release is assessed on a versioned set covering routine, ambiguous, adverse, and adversarial cases. |
| FR-07 | Monitoring | Log intent, source IDs, model/config version, latency, outcome, escalation, and reviewed quality signals. |
| FR-08 | Fallback | If retrieval fails, confidence is low, or the model/service is unavailable, present a safe fallback and/or escalate. |

## Non-functional requirements

- **Traceability:** capture the source document version and model/prompt version for each evaluated output.
- **Security:** use authenticated APIs and approved data handling; never place secrets in logs.
- **Reliability:** define availability, latency, rate-limit, and fallback expectations before pilot.
- **Accessibility:** plain language, understandable next steps, keyboard-friendly interface.
- **Maintainability:** separate policy content from code; version policy updates and regression-test them.

## Key assumptions and dependencies

- Policy content has an authoritative owner and approval lifecycle.
- Account-specific data is not available to this portfolio demo.
- Any production account integration would require identity/access controls, privacy review, audit logging, and security approval.
- The business case depends on actual contact volumes, loaded labor costs, containment, AI cost, and integration costs that must be validated.

## Launch acceptance gates (proposed, not actual issuer standards)

- Zero critical privacy or unsupported-action failures in the release test set.
- Escalation recall meets the risk team's predefined target for high-risk intents.
- Groundedness and answer quality meet thresholds set from human-reviewed examples.
- No worsening in customer complaints, repeat contact, or CSAT during the controlled pilot.
- A documented rollback, incident owner, and policy-update process are in place.
