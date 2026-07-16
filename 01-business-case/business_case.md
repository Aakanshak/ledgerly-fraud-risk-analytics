# Business case

## Decision at stake

Select the model and operating threshold for automated declines. The decision will be based on total expected dollar cost and tested before full rollout.

## Constraints and guardrails

- Keep legitimate false-decline rate below 2.0% during the experiment.
- Monitor complaint rate and segment-level false declines; no aggregate win can justify an unacceptable subgroup outcome.
- Use only features available at transaction decision time.
- Train on earlier months and test on later months; do not use random splitting.
- Treat manual review capacity as a future optimization rather than silently assuming unlimited capacity.

## Hypotheses

- H1: Card-not-present categories and selected cross-border routes have materially higher fraud rates.
- H2: High hourly/daily velocity, device/IP switching, account age, amount, and off-hours behavior improve risk ranking.
- H3: Gradient boosting improves PR-AUC over logistic regression because risk interactions are nonlinear.
- H4: A dollar-optimal threshold differs from 0.50 and saves money without exceeding the false-decline guardrail.
- H5: A four-week traffic experiment reproduces directionally similar savings to offline estimates.

## Assumptions to validate

| Assumption | Baseline | Sensitivity |
|---|---:|---|
| Lost margin on false decline | 2.9% of amount | 1.5%–5.0% |
| Support/CX cost per false decline | $8 | $4–$15 |
| Chargeback fee | $15 | $10–$25 |
| Current threshold | 0.50 | Compared across full curve |
| Fraud-rate target | 1%–3% | Calibrated in generator |

## Intentional leakage control

Random splits let later fraud patterns inform earlier training and overstate deployment performance. Ledgerly trains on the first nine months, validates on the next month, and evaluates once on the final two months.

## So what?

The approval decision is explicitly tied to economics and guardrails. Model quality matters only insofar as it produces a safer, lower-cost operating policy on future traffic.
