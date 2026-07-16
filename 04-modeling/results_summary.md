# Model results summary

## Out-of-time performance

| Model | ROC-AUC | PR-AUC | Brier score |
|---|---:|---:|---:|
| Logistic regression | 0.627 | 0.059 | 0.0295 |
| Gradient boosting | 0.623 | 0.061 | 0.0294 |

Gradient boosting is selected for decisioning because it produced the stronger PR-AUC (0.061 vs. 0.059) and the lowest feasible downstream dollar cost. Its useful signal is intentionally modest: fraud and legitimate high-velocity behavior overlap, which is more credible than near-perfect synthetic separation. Top permutation signals include ip_country, merchant_category, transaction_hour, log_amount, transactions_per_day.

At a literal 0.50 threshold, both calibrated models flag almost nothing. That is not a failure of calibration; it demonstrates why 0.50 is an arbitrary operating convention for a rare event. The dollar optimizer selects 0.101.

## Why accuracy is misleading

Fraud prevalence is 2.65%; predicting “legitimate” every time would be 97.35% accurate while catching zero fraud. PR-AUC, recall, calibration, and business cost are therefore more meaningful.

## Leakage control

Training uses January–September, calibration uses October, and the untouched evaluation set is November–December. This mirrors prospective deployment and prevents future patterns from leaking backward.

## So what?

The model is valuable because its ranking supports a lower-cost policy—not because it creates an impressive accuracy headline.
