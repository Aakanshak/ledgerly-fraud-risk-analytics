"""Simulate a reproducible 20% stricter-threshold test and analyze outcomes."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

ROOT=Path(__file__).resolve().parent.parent
def diff_test(x1,n1,x0,n0):
    pooled=(x1+x0)/(n1+n0); se=np.sqrt(pooled*(1-pooled)*(1/n1+1/n0)); z=(x1/n1-x0/n0)/se if se else 0
    return float(z),float(2*norm.sf(abs(z)))

def run(seed=42):
    rng=np.random.default_rng(seed); pred=pd.read_csv(ROOT/"04-modeling"/"artifacts"/"gradient_boosting_test_predictions.csv")
    opt=json.loads((ROOT/"05-cost-based-decisioning"/"outputs"/"optimal_threshold.json").read_text())
    exp=pd.concat([pred]*3,ignore_index=True).sample(n=min(100000,len(pred)*3),replace=False,random_state=seed).reset_index(drop=True)
    exp["group"]=np.where(rng.random(len(exp))<.20,"test","control")
    exp["threshold"]=np.where(exp.group.eq("test"),opt["optimal_threshold"],opt["current_threshold"])
    exp["blocked"]=exp.score>=exp.threshold
    exp["fraud_loss"]=np.where((exp.is_fraud.eq(1))&(~exp.blocked),exp.amount+15+exp.resolution_cost,0)
    exp["false_decline"]=(exp.is_fraud.eq(0))&exp.blocked
    rows=[]
    for g,d in exp.groupby("group"):
        legit=d.is_fraud.eq(0); rows.append({"group":g,"transactions":len(d),"fraud_transactions":int(d.is_fraud.sum()),"fraud_loss":d.fraud_loss.sum(),"fraud_loss_per_transaction":d.fraud_loss.sum()/len(d),"false_declines":int(d.false_decline.sum()),"false_decline_rate":d.loc[legit,"false_decline"].mean()})
    summary=pd.DataFrame(rows); test=summary.set_index("group").loc["test"]; control=summary.set_index("group").loc["control"]
    z,p=diff_test(int(test.false_declines),int(test.transactions-test.fraud_transactions),int(control.false_declines),int(control.transactions-control.fraud_transactions))
    result={"groups":summary.to_dict("records"),"fraud_loss_rate_change":float(test.fraud_loss_per_transaction/control.fraud_loss_per_transaction-1),"incremental_false_decline_rate":float(test.false_decline_rate-control.false_decline_rate),"false_decline_z":z,"false_decline_p_value":p,"model_predicted_test_period_savings":opt["test_period_savings"]}
    out=Path(__file__).parent/"outputs"; out.mkdir(exist_ok=True); summary.to_csv(out/"experiment_summary.csv",index=False); (out/"experiment_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    dash=ROOT/"08-dashboard"/"app_data"; summary.to_csv(dash/"experiment_summary.csv",index=False); (dash/"experiment_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2)); print("So what? The test estimates realized loss reduction and makes the customer-experience price visible before full rollout.")
    return result
if __name__=="__main__": run()
