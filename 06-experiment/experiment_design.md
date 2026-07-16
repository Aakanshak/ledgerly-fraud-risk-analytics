# Threshold experiment design

## Objective

Validate that the cost-optimal model threshold reduces fraud loss per transaction without breaching a 2.0% legitimate false-decline guardrail.

## Design

- Population: otherwise eligible payment attempts.
- Randomization unit: user, persisted for the experiment to prevent cross-arm contamination.
- Allocation: 20% test / 80% control for four weeks.
- Control: current 0.50 threshold. Test: offline dollar-optimal threshold.
- Primary outcome: net fraud loss per processed dollar, after chargeback and false-decline cost.
- Guardrails: legitimate false-decline rate, complaint contacts per 1,000 attempts, approval rate, manual-review volume, and segment disparities.
- Analysis: intention-to-treat with confidence intervals; compare realized savings with the offline projection.

## Operational checks

Confirm score parity, stable randomization, sample-ratio match, logging completeness, no overlapping risk-rule change, and kill-switch ownership. Use leading fraud labels provisionally and re-read results after chargeback maturation.

## Decision rule

Roll out only if loss economics improve directionally, the false-decline rate remains below 2.0%, no critical segment guardrail is breached, and the result survives chargeback maturation.

## So what?

Offline optimization proposes a policy; randomized exposure determines whether it survives real customer behavior, operations, and delayed fraud labels.
