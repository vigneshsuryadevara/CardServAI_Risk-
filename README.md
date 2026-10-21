# CardServ AI — Servicing Intelligence & Optimization

**A portfolio project for a Senior Business Analyst / AI Product Strategist role**

CardServ AI is a portfolio prototype for a hypothetical credit-card servicing experience. It brings together contact analytics, policy retrieval, evaluation, a scenario-based business case, and an illustrative risk-and-launch workflow.

> **Important:** This is an independent portfolio concept. It is not affiliated with, endorsed by, or connected to Capital One. All contact records and evaluation questions are synthetic. Knowledge-base content is illustrative—not issuer policy. It has no access to real accounts or payment systems, and all financial projections are assumptions rather than actual savings.

## What is included

- **Interactive Streamlit app** with executive overview, contact analytics, AI assistant, evaluation lab, business case, and product-spec pages.
- **5,000 synthetic servicing contacts** with intent, channel, handling time, repeat-contact flag, transfer, resolution, CSAT, and risk tier.
- **Policy retrieval prototype** using TF-IDF retrieval over six illustrative policy documents, transparent intent routing, safe response templates, citations, and escalation recommendations.
- **Optional OpenAI response drafting** for experimentation. Offline safe mode works without an API key.
- **260-case core regression suite** plus a **42-case challenge suite** that uses more varied phrasing and account-action / privacy cases.
- **Business case simulator** with adjustable annual contact volume, eligible intents, containment, loaded labor cost, model cost, platform cost, and implementation investment.
- **AI Risk & Governance Control Center** with a use-case register, inherent/residual risk scoring, required controls, evaluation-linked launch gates, simulated review decisions, monitoring thresholds, and incident logging/export.
- **Product artifacts** covering strategy, functional requirements, evaluation plan, risk framework, launch gates, and the business case.
- **Five-minute presentation guide** for a focused hiring-manager walkthrough and clear discussion of limitations.
- **Unit tests** for data integrity, routing, safety response, repeatability, and business-case calculations.

## Run locally

Use Python 3.10–3.12. From this project directory:

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL; open it in your browser. No API key is required for the offline demo.

## Optional: enable OpenAI response drafting

1. Copy `.env.example` to `.env` or set the environment variables in your terminal.
2. Set `OPENAI_API_KEY` to your own key, and optionally set `OPENAI_MODEL`.
3. Restart Streamlit and enable the OpenAI response toggle on the **AI assistant** page.

The app does not automatically load a `.env` file; set environment variables in your shell or use an approved local environment loader. Do not commit API keys. Do not enter real customer data. LLM output still needs separate testing and review before any real use.

## Re-run data generation, evaluation, and tests

```bash
python scripts/generate_data.py
python scripts/run_evaluation.py
pytest -q
```

`run_evaluation.py` writes reproducible outputs to `artifacts/`, including core and challenge evaluation results, contact analytics summary, business-case scenarios, and a JSON metrics summary.

## How the prototype works

```text
Synthetic contact data
        ↓
Contact analytics ───────→ Use-case prioritization + business-case assumptions
        ↓
Customer question
        ↓
Rule-based intent routing + TF-IDF policy retrieval
        ↓
Offline safe response templates (or optional OpenAI drafting)
        ↓
Source display + escalation recommendation
        ↓
Core regression tests + challenge tests + operational launch gates
```

### Design choices

- The **offline default** is deterministic so the project runs without paid APIs and test results are repeatable.
- The retriever displays the policy document IDs and relevance scores to make evidence inspection possible.
- Sensitive or account-specific requests are routed to an authenticated servicing workflow rather than being answered as if the system had account access.
- Deterministic policy and financial logic should sit outside the language model. The demo intentionally does not calculate real balances, interest charges, eligibility, or payment outcomes.
- The business case lets the user supply projected annual contact volume separately. The 5,000-row synthetic dataset informs intent mix and handling-time examples; it should not be mistaken for issuer-wide annual volume.

## Evaluation results

The included suite is a small, hand-authored demo test set, not a representative benchmark. When generated with the included rules and documents, the current deterministic checks report:

| Metric | Core regression suite | Challenge suite |
|---|---:|---:|
| Test cases | 260 | 42 |
| Intent accuracy | 100% | 97.6% |
| Expected-source retrieval hit rate | 100% | 100% |
| Escalation precision | 100% | 100% |
| Escalation recall | 100% | 100% |
| Escalation decision accuracy | 100% | 100% |
| Citation rate | 100% | 97.6% |

These results show that the current rules pass the included examples; they **do not** establish semantic correctness, factual reliability, regulatory compliance, production safety, or customer benefit. The challenge set includes a payment-pending phrasing that is routed to the generic account-specific fallback rather than the payment-processing intent; it remains safely escalated but is a known taxonomy improvement. The off-topic weather question correctly avoids an unsupported policy citation. Several labels and keywords are hand-authored together, so the results are susceptible to test-set overfitting. A real evaluation should use approved, de-identified historical examples, an independently labeled holdout set, human-reviewed answer quality, red-team cases, and pilot outcome measures. `artifacts/evaluation_summary.json` is the reproducible source for the latest locally generated metric values.

## Business-case model

The app calculates:

- **Annual in-scope contacts** = projected annual contact volume × share of selected intents.
- **Annual contained contacts** = in-scope contacts × target containment rate.
- **Gross labor value** = contained contacts × average in-scope handle time ÷ 60 × loaded labor cost per hour.
- **Steady-state net benefit** = gross labor value − AI variable cost − annual platform / operations cost.
- **Year 1 net benefit** = steady-state net benefit − one-time build / integration cost.

The default annual volume is an illustrative input of 250,000, not a fact. The model excludes or simplifies staffing constraints, ramp effects, discounting, false containment, compliance expense, integration complexity, and other costs that must be validated with Finance and Operations.

## Suggested interview walkthrough

1. Start with the **Contact analytics** page and explain how you would rank intents using volume, handling time, repeat contact, transfers, and risk.
2. Open the **AI assistant** and demonstrate a source-backed answer alongside a sensitive request that should escalate.
3. Open the **Evaluation lab** and show both the regression suite and the challenge case results. Explain why perfect results on a curated test set are not enough and how you'd build an independent evaluation set.
4. Open **AI Risk & Governance**. Walk through the use-case inventory, show how missing controls or failed tests block the launch gate, then test a monitoring breach and its recommended response.
5. Adjust the **Business case** assumptions. Discuss which inputs Finance and Operations would need to validate before making an investment decision.
6. Finish with the **Product spec** and explain the requirements, risk framework, monitoring, and rollback plan.

## Repository layout

```text
app.py                         Streamlit application
src/cardserv_ai/assistant.py   Intent routing, retrieval, response safety, optional LLM path
src/cardserv_ai/data.py        Synthetic contact and evaluation data utilities
src/cardserv_ai/evaluation.py  Repeatable heuristic evaluation metrics
src/cardserv_ai/business_case.py Business-case model and scenarios
data/synthetic_contacts.csv   5,000 synthetic contact records
data/evaluation_cases.csv     Core regression scenarios
data/challenge_cases.csv      More varied challenge scenarios
data/knowledge_base/          Illustrative sample policies
docs/                          Product strategy, requirements, evaluation, business case
scripts/                       Data generation and evaluation commands
tests/test_core.py             Automated tests
artifacts/                      Reproducible CSV / JSON summaries
```

## Hosting

See [DEPLOYMENT.md](DEPLOYMENT.md) for the recommended Streamlit Community Cloud steps and the limitations of session-based demo records. See [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md) for a five-minute walkthrough. The app can run without API credentials.

## Recommended next improvements

- Replace keyword intent routing with a measured classifier and compare the accuracy / latency / cost trade-off.
- Add a human-reviewed answer rubric for correctness, completeness, tone, grounding, and severity.
- Add adversarial prompt-injection, irrelevant query, stale-policy, and retrieval-failure tests.
- Log versioned prompts, policy revisions, retrieval scores, latency, model costs, feedback, and human-review outcomes.
- Add a pilot experiment design and estimate confidence intervals for customer and operational outcomes.
