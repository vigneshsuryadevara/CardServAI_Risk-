# AI Evaluation and Monitoring Plan

## Evaluation set

The included balanced set is synthetic and intended to demonstrate test design, not to represent real customer language or production performance. It covers eight servicing intents plus account-specific requests. Before real use, expand it with approved, de-identified examples and human-reviewed expected answers.

## Offline metrics

- **Intent accuracy:** predicted intent matches the labeled intent.
- **Retrieval hit rate:** expected policy source appears in the top retrieved documents.
- **Escalation precision:** among cases escalated by the system, share expected to escalate.
- **Escalation recall:** among cases expected to escalate, share actually escalated.
- **Escalation accuracy:** share of all cases where the escalation decision matches the label.
- **Citation rate:** responses include visible source attribution when sources are retrieved.
- **Privacy guardrail pass rate:** simple rubric check for account-specific and sensitive cases.

These checks are intentionally simple, transparent heuristics. They do not establish semantic correctness, legal compliance, or production readiness. Human review is required for factual correctness, helpfulness, tone, completeness, and critical failure severity.

## Test categories

1. Common phrasing and paraphrases.
2. Ambiguous questions with multiple possible intents.
3. Requests for balances, transactions, payments, fee reversals, and account changes.
4. Fraud, lost/stolen-card, and dispute scenarios.
5. Prompt-injection attempts asking the system to ignore policy or reveal secrets.
6. Unsupported-policy questions where the correct behavior is to acknowledge uncertainty.
7. Retrieval failures, stale policy versions, malformed inputs, and model-service failures.

## Monitoring dashboard

Track intent mix, retrieval failures, answer quality from sampled reviews, escalation rate, confirmed resolution, repeat contact within the defined window, transfer rate, CSAT, complaints, safety events, latency, cost, and drift. Slice by intent, channel, policy version, model version, and customer segment where permitted.

## Proposed operational response

- **Critical safety/privacy event:** immediately disable the affected path, preserve audit evidence, and notify the incident owner.
- **Quality regression:** pause expansion, inspect failed cases, correct policy/retrieval/prompt logic, and rerun regression tests.
- **Drift or new intent:** collect reviewed examples, update labels and knowledge content, and re-evaluate before release.
- **Missing or weak retrieval:** safe fallback; never force a substantive answer from irrelevant documents.
