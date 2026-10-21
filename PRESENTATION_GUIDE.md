# CardServ AI — 5-minute review guide

The goal is to explain the decisions behind the prototype, not to click through every page.

## 1. Start with the servicing problem (45 seconds)

Open **Executive overview**. Explain that the 5,000 contacts are synthetic and show how volume, handling time, repeat contact, transfer, and customer satisfaction can help prioritize opportunities. High volume alone is not sufficient; the proposed use case also needs a clear policy basis and a safe fallback.

## 2. Show how an answer is supported (60 seconds)

Open **AI assistant** and ask: “Why was I charged a late fee?” Show the retrieved policy text and source identifiers. Then ask for an exact payment status or account balance and show why the prototype will not pretend to have account access.

## 3. Show what testing tells you—and what it doesn't (60 seconds)

Open **Evaluation lab**. Explain the difference between the core regression suite and the challenge suite. Point out that the test set is hand-authored and synthetic, so these metrics are evidence about the included scenarios only. They do not prove live customer resolution or policy correctness.

## 4. Make the risk process tangible (90 seconds)

Open **AI risk & governance**. Select **Policy explanation assistant**. Show the use-case register, inherent/residual risk ratings, and the controls that still need evidence. Then change a proposed evaluation threshold above a reported test result or leave a critical control incomplete to demonstrate why launch status becomes blocked. In the monitoring section, tick **Privacy / security event reported** and explain the recommended containment, human routing, investigation, and retest steps.

## 5. Connect it to execution and value (45 seconds)

Open **Business case** and change one or two assumptions. Explain that containment is a hypothesis to validate against confirmed resolution, repeat contact, customer outcomes, and operating costs—not an assumed saving. Finish by showing the requirements and risk framework in **Product spec**.

## Closing point

“The central design choice is to make the evidence and decision process visible: what the assistant can do, what evidence supports it, what controls are missing, and what the team should do when results deteriorate. This is a prototype of that workflow, not a production deployment.”

## Known limitations to state directly

- Synthetic contact data and illustrative knowledge-base content.
- Rule-based intent classification and TF-IDF source retrieval.
- The included evaluation metrics are simple checks against hand-authored cases.
- The risk inventory, controls, thresholds, decisions, and incident signals are illustrative.
- Monitoring inputs are simulated; session incidents are not stored as a durable audit log.
- No actual Capital One systems, policies, account data, financial results, or formal approvals are represented.
