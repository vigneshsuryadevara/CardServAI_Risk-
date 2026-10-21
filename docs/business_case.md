# Illustrative Business Case

This is a scenario model, not a forecast for Capital One or any other issuer. The default 250,000 annual-contact input is a configurable illustration, not a fact. The synthetic sample informs intent mix and handling-time distribution only. All volume, labor, containment, and cost assumptions must be replaced with validated finance and operations data before a funding decision.

## Model logic

1. Apply a separate projected annual contact volume assumption, validated by operations/finance; the synthetic contact rows provide only an example of intent mix and handling-time distribution.
2. Estimate in-scope contacts from the selected intent share.
3. Estimate contained contacts as in-scope volume × target containment rate.
4. Estimate gross labor value as contained contacts × average handling minutes ÷ 60 × loaded hourly cost.
5. Subtract AI variable cost for every in-scope interaction, annual platform cost, and one-time build cost for the Year 1 view.

**Steady-state net benefit** = gross labor savings − annual AI variable cost − annual platform cost.

**Year 1 net benefit** = steady-state net benefit − one-time build cost.

## Risks and omissions to discuss

- The model treats successful containment as avoided labor value; actual labor savings depend on staffing, demand, and whether time is redeployed.
- It excludes customer lifetime value, implementation delays, compliance/control expense, vendor minimums, integration complexity, and opportunity cost unless represented in inputs.
- Quality regressions or false containment can erase savings and harm customers.
- Savings should be validated through a controlled pilot and finance-approved methodology.
