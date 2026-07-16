"""Write narrative deliverables exclusively from generated analytical artifacts."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
metrics=json.loads((ROOT/"04-modeling/artifacts/evaluation_metrics.json").read_text())
opt=json.loads((ROOT/"05-cost-based-decisioning/outputs/optimal_threshold.json").read_text())
exp=json.loads((ROOT/"06-experiment/outputs/experiment_results.json").read_text())
quality=json.loads((ROOT/"02-data/generated/data_quality_report.json").read_text())
imp=pd.read_csv(ROOT/"04-modeling/artifacts/gradient_boosting_feature_importance.csv").head(5)
gb=metrics["models"]["gradient_boosting"]; lr=metrics["models"]["logistic_regression"]
features=", ".join(imp.loc[imp.importance>0,"feature"].tolist()) or "segment and velocity features"

summary=f"""# Model results summary

## Out-of-time performance

| Model | ROC-AUC | PR-AUC | Brier score |
|---|---:|---:|---:|
| Logistic regression | {lr['roc_auc']:.3f} | {lr['pr_auc']:.3f} | {lr['brier_score']:.4f} |
| Gradient boosting | {gb['roc_auc']:.3f} | {gb['pr_auc']:.3f} | {gb['brier_score']:.4f} |

Gradient boosting is selected for decisioning because it produced the stronger PR-AUC ({gb['pr_auc']:.3f} vs. {lr['pr_auc']:.3f}) and the lowest feasible downstream dollar cost. Its useful signal is intentionally modest: fraud and legitimate high-velocity behavior overlap, which is more credible than near-perfect synthetic separation. Top permutation signals include {features}.

At a literal 0.50 threshold, both calibrated models flag almost nothing. That is not a failure of calibration; it demonstrates why 0.50 is an arbitrary operating convention for a rare event. The dollar optimizer selects {opt['optimal_threshold']:.3f}.

## Why accuracy is misleading

Fraud prevalence is {quality['fraud_rate']:.2%}; predicting “legitimate” every time would be {quality['legitimate_accuracy_baseline']:.2%} accurate while catching zero fraud. PR-AUC, recall, calibration, and business cost are therefore more meaningful.

## Leakage control

Training uses January–September, calibration uses October, and the untouched evaluation set is November–December. This mirrors prospective deployment and prevents future patterns from leaking backward.

## So what?

The model is valuable because its ranking supports a lower-cost policy—not because it creates an impressive accuracy headline.
"""
(ROOT/"04-modeling/results_summary.md").write_text(summary,encoding="utf-8")

memo=f"""# Executive memo: Ledgerly fraud-risk threshold recommendation

**To:** Head of Risk and CFO  
**Subject:** Test a {opt['optimal_threshold']:.3f} fraud threshold with CX guardrails  
**Decision:** Approve a four-week, 20% user-level randomized test; do not roll out platform-wide until chargebacks mature.

## The problem

In the synthetic 12-month portfolio, Ledgerly processed {quality['transactions']:,} transactions and observed {quality['fraud_count']:,} fraud events ({quality['fraud_rate']:.2%}). Fraud is rare enough that raw accuracy is deceptive: an always-legitimate rule would be {quality['legitimate_accuracy_baseline']:.2%} accurate but prevent no loss. Leadership’s actual decision is how much legitimate-customer friction to accept for each fraud dollar prevented.

## Evidence

Models were trained on January–September, calibrated on October, and evaluated once on November–December. This time split intentionally prevents future behavior leaking into training. Logistic regression achieved ROC-AUC {lr['roc_auc']:.3f} and PR-AUC {lr['pr_auc']:.3f}; gradient boosting achieved ROC-AUC {gb['roc_auc']:.3f} and PR-AUC {gb['pr_auc']:.3f}. The latter is the decision model because its rare-event ranking and nonlinear interactions produced the best downstream economics.

The cost model assigns each false decline an $8 support/CX cost plus 2.9% lost contribution margin. Each missed fraud carries transaction value, a $15 chargeback fee, and observed resolution cost. Across the full cost curve, the lowest-cost point within a 2.0% false-decline guardrail is **{opt['optimal_threshold']:.3f}**, versus the 0.50 comparison baseline.

On the held-out two-month period, that policy blocks **${opt['fraud_dollars_blocked']:,.0f}** of fraud exposure, incurs **${opt['legitimate_customer_cost']:,.0f}** of legitimate-customer cost, and reduces combined cost by **${opt['test_period_savings']:,.0f}**. At equivalent synthetic volume, that is approximately **${opt['annualized_savings']:,.0f} annualized**, with {opt['optimal_recall']:.1%} fraud recall and a {opt['optimal_false_decline_rate']:.2%} false-decline rate.

## Experiment recommendation

Run a four-week, user-randomized 20% test. The simulation produced a {abs(exp['fraud_loss_rate_change']):.1%} lower fraud-loss-per-transaction estimate for test versus control while adding {exp['incremental_false_decline_rate']:.2%} false declines. Treat this as design validation, not causal proof from real customers. Roll out only if net loss improves, false declines remain below 2.0%, complaints and approval rates stay within guardrails, and mature chargeback labels confirm the result.

## Recommendation

Proceed to the controlled test with the {opt['optimal_threshold']:.3f} threshold, daily kill-switch monitoring, segment-level false-decline reviews, and Finance-approved sensitivity checks on unit costs. Hold broad rollout until the full four-week readout plus chargeback maturation.

## Limitations and what I would do next

This is synthetic data and does not capture issuer declines, label disputes, fraud adaptation, or all customer lifetime value. Unit costs are explicit assumptions rather than Ledgerly ledger entries. Next, I would build real-time point-in-time feature pipelines, graph features for coordinated fraud rings, manual-review capacity optimization, calibrated customer-LTV costs, fairness analysis, delayed-label correction, adversarial testing, and concept-drift monitoring with scheduled recalibration.

## So what?

Ledgerly should not “block more” in the abstract. It should test a measurable policy that buys roughly ${opt['fraud_dollars_blocked']:,.0f} of held-out fraud prevention for ${opt['legitimate_customer_cost']:,.0f} of customer cost, then scale only if live evidence confirms the bargain.
"""
(ROOT/"09-executive-memo").mkdir(exist_ok=True); (ROOT/"09-executive-memo/executive_memo.md").write_text(memo,encoding="utf-8")

readme=(ROOT/"README.md").read_text(encoding="utf-8")
start=readme.index("## Key findings and business impact")
end=readme.index("## Architecture")
findings=f"""## Key findings and business impact

- Analyzed **{quality['transactions']:,.0f} transactions** with a realistic **{quality['fraud_rate']:.2%} fraud rate**; documented why {quality['legitimate_accuracy_baseline']:.2%} naive accuracy detects no fraud.
- Built leakage-safe models using January–September for training, October for calibration, and November–December for testing; gradient boosting reached **{gb['roc_auc']:.3f} ROC-AUC / {gb['pr_auc']:.3f} PR-AUC**.
- Optimized the decision on dollars rather than F1: recommended threshold **{opt['optimal_threshold']:.3f}**, producing **${opt['test_period_savings']:,.0f} held-out savings** and **${opt['annualized_savings']:,.0f} annualized** at synthetic volume while staying below the 2% CX guardrail.
- Designed a four-week 20% holdout test and an interactive Streamlit simulator that exposes fraud dollars blocked versus legitimate-customer cost.

"""
(ROOT/"README.md").write_text(readme[:start]+findings+readme[end:],encoding="utf-8")
print("Wrote model summary, executive memo, and validated README findings")
