# Discovery document

## Situation

Ledgerly is scaling payment volume while fraud and chargeback loss is rising. The baseline data is designed around a 1%–3% transaction fraud rate, with loss concentrated in selected merchant categories, geographies, new accounts, and velocity spikes.

## Working economics

- False positive (declined legitimate payment): lost contribution margin equal to 2.9% of payment value plus $8 support/CX cost.
- False negative (approved fraud): transaction amount lost plus a $15 chargeback fee and observed resolution expense.
- Current production-style threshold: 0.50. This is a comparison baseline, not assumed optimal.

## Stakeholders

| Stakeholder | Primary objective | Main concern |
|---|---|---|
| Head of Risk | Reduce fraud and chargeback loss | Under-blocking and regulatory exposure |
| Growth | Preserve authorization and conversion | False declines and customer churn |
| CFO | Improve risk-adjusted unit economics | Gross savings that ignore CX cost |
| Operations | Keep manual review manageable | Queue volume and investigation cost |
| Compliance | Consistent, explainable controls | Disparate or untraceable decisions |

## Discovery questions

1. Where is fraud concentrated by time, category, geography, amount, and velocity?
2. Which model ranks risk best on future months, and is it calibrated enough for dollar decisions?
3. What threshold minimizes total false-positive and false-negative cost?
4. Do simulated experiment outcomes agree with offline projected savings without breaching guardrails?

## So what?

Risk and Growth are not choosing between “safe” and “unsafe”; they are choosing which type of error Ledgerly is willing to buy, at what dollar cost, and with which customer guardrails.
