# Executive memo: Ledgerly fraud-risk threshold recommendation

**To:** Head of Risk and CFO  
**Subject:** Test a 0.101 fraud threshold with CX guardrails  
**Decision:** Approve a four-week, 20% user-level randomized test; do not roll out platform-wide until chargebacks mature.

## The problem

In the synthetic 12-month portfolio, Ledgerly processed 200,000.0 transactions and observed 5,293.0 fraud events (2.65%). Fraud is rare enough that raw accuracy is deceptive: an always-legitimate rule would be 97.35% accurate but prevent no loss. Leadership’s actual decision is how much legitimate-customer friction to accept for each fraud dollar prevented.

## Evidence

Models were trained on January–September, calibrated on October, and evaluated once on November–December. This time split intentionally prevents future behavior leaking into training. Logistic regression achieved ROC-AUC 0.627 and PR-AUC 0.059; gradient boosting achieved ROC-AUC 0.623 and PR-AUC 0.061. The latter is the decision model because its rare-event ranking and nonlinear interactions produced the best downstream economics.

The cost model assigns each false decline an $8 support/CX cost plus 2.9% lost contribution margin. Each missed fraud carries transaction value, a $15 chargeback fee, and observed resolution cost. Across the full cost curve, the lowest-cost point within a 2.0% false-decline guardrail is **0.101**, versus the 0.50 comparison baseline.

On the held-out two-month period, that policy blocks **$10,624** of fraud exposure, incurs **$5,723** of legitimate-customer cost, and reduces combined cost by **$4,901**. At equivalent synthetic volume, that is approximately **$29,408 annualized**, with 7.7% fraud recall and a 1.68% false-decline rate.

## Experiment recommendation

Run a four-week, user-randomized 20% test. The simulation produced a 3.4% lower fraud-loss-per-transaction estimate for test versus control while adding 1.60% false declines. Treat this as design validation, not causal proof from real customers. Roll out only if net loss improves, false declines remain below 2.0%, complaints and approval rates stay within guardrails, and mature chargeback labels confirm the result.

## Recommendation

Proceed to the controlled test with the 0.101 threshold, daily kill-switch monitoring, segment-level false-decline reviews, and Finance-approved sensitivity checks on unit costs. Hold broad rollout until the full four-week readout plus chargeback maturation.

## Limitations and what I would do next

This is synthetic data and does not capture issuer declines, label disputes, fraud adaptation, or all customer lifetime value. Unit costs are explicit assumptions rather than Ledgerly ledger entries. Next, I would build real-time point-in-time feature pipelines, graph features for coordinated fraud rings, manual-review capacity optimization, calibrated customer-LTV costs, fairness analysis, delayed-label correction, adversarial testing, and concept-drift monitoring with scheduled recalibration.

## So what?

Ledgerly should not “block more” in the abstract. It should test a measurable policy that buys roughly $10,624 of held-out fraud prevention for $5,723 of customer cost, then scale only if live evidence confirms the bargain.
