"""Choose the threshold that minimizes total cost subject to CX guardrails."""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from cost_translation import evaluate_thresholds

def run(model="gradient_boosting", current_threshold=.50, max_false_decline_rate=.02):
    pred=pd.read_csv(ROOT/"04-modeling"/"artifacts"/f"{model}_test_predictions.csv")
    curve=evaluate_thresholds(pred)
    feasible=curve[curve.false_decline_rate<=max_false_decline_rate]
    optimal=feasible.loc[feasible.total_cost.idxmin()]
    current=evaluate_thresholds(pred,[current_threshold]).iloc[0]
    result={"model":model,"current_threshold":current_threshold,"optimal_threshold":float(optimal.threshold),"max_false_decline_rate":max_false_decline_rate,"current_total_cost":float(current.total_cost),"optimal_total_cost":float(optimal.total_cost),"test_period_savings":float(current.total_cost-optimal.total_cost),"annualized_savings":float((current.total_cost-optimal.total_cost)*6),"optimal_false_decline_rate":float(optimal.false_decline_rate),"optimal_recall":float(optimal.recall),"optimal_precision":float(optimal.precision),"fraud_dollars_blocked":float(optimal.fraud_dollars_blocked),"legitimate_customer_cost":float(optimal.legitimate_customer_cost),"residual_fraud_loss":float(optimal.residual_fraud_loss)}
    out=HERE/"outputs"; out.mkdir(exist_ok=True); curve.to_csv(out/"threshold_cost_curve.csv",index=False); (out/"optimal_threshold.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    dash=ROOT/"08-dashboard"/"app_data"; curve.to_csv(dash/"threshold_cost_curve.csv",index=False); (dash/"optimal_threshold.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2)); print("So what? The recommended threshold is the lowest-cost feasible policy, not the point with the prettiest classification metric.")
    return result
if __name__=="__main__": run()
