# Risk product metrics framework

## North-star metric

**Net fraud loss as a percentage of processed payment volume** = (residual fraud loss + chargeback fees + false-decline contribution/support cost + review cost) / processed volume.

This prevents teams from declaring victory by blocking more payments while shifting cost into customer experience and lost growth.

## Driver metrics

- Fraud dollars blocked and residual fraud loss
- Recall at the operating threshold
- Precision / analyst yield for reviewed transactions
- Chargeback rate and loss per approved transaction
- Expected calibration error and score drift

## Guardrails

- Legitimate false-decline rate ≤ 2.0%
- Approval-rate change by category, geography, tenure, and amount
- Customer complaint contacts per 1,000 attempts
- Repeat-purchase and 30-day retention after a decline
- Manual-review queue SLA and cost
- Model performance and fairness stability by segment

## Review cadence

Daily operational alerts, weekly threshold and queue review, monthly calibration/drift review, and quarterly policy re-optimization with Finance-approved unit costs.

## So what?

The framework rewards lower total loss, not indiscriminate blocking, and gives Growth, Risk, Finance, and Operations a shared scorecard.
