"""Train, calibrate, evaluate, and persist both models."""
from __future__ import annotations
import json, sys
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import average_precision_score, roc_auc_score, precision_score, recall_score, confusion_matrix, brier_score_loss, roc_curve, precision_recall_curve
from sklearn.inspection import permutation_importance

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from preprocessing import FEATURES, time_split
from logistic_regression_model import build_model as logistic
from gradient_boosting_model import build_model as boosting

def metrics(y, p, threshold=.5):
    pred=p>=threshold
    return {"roc_auc":roc_auc_score(y,p),"pr_auc":average_precision_score(y,p),"precision_at_0_5":precision_score(y,pred,zero_division=0),"recall_at_0_5":recall_score(y,pred),"brier_score":brier_score_loss(y,p),"confusion_matrix":confusion_matrix(y,pred).tolist()}

def run():
    df=pd.read_parquet(ROOT/"03-etl-and-analysis"/"outputs"/"model_features.parquet"); s=time_split(df)
    out=HERE/"artifacts"; out.mkdir(exist_ok=True); dash=ROOT/"08-dashboard"/"app_data"; dash.mkdir(parents=True,exist_ok=True)
    summary={"split":{"train_rows":len(s.train),"validation_rows":len(s.validation),"test_rows":len(s.test),"train_end":str(s.train.timestamp.max()),"test_start":str(s.test.timestamp.min()),"test_fraud_rate":s.test.is_fraud.mean()},"models":{}}
    curves=[]
    for name,builder in [("logistic_regression",logistic),("gradient_boosting",boosting)]:
        base=builder(); base.fit(s.train[FEATURES],s.train.is_fraud)
        calibrated=CalibratedClassifierCV(FrozenEstimator(base),method="sigmoid"); calibrated.fit(s.validation[FEATURES],s.validation.is_fraud)
        p=calibrated.predict_proba(s.test[FEATURES])[:,1]
        joblib.dump(calibrated,out/f"{name}.joblib")
        pd.DataFrame({"transaction_id":s.test.transaction_id,"timestamp":s.test.timestamp,"amount":s.test.amount,"is_fraud":s.test.is_fraud,"resolution_cost":s.test.resolution_cost,"score":p,"model":name}).to_csv(out/f"{name}_test_predictions.csv",index=False)
        summary["models"][name]=metrics(s.test.is_fraud,p)
        sample=s.test.sample(n=min(6000,len(s.test)),random_state=42)
        importance=permutation_importance(calibrated,sample[FEATURES],sample.is_fraud,n_repeats=3,random_state=42,scoring="average_precision")
        pd.DataFrame({"feature":FEATURES,"importance":importance.importances_mean}).sort_values("importance",ascending=False).to_csv(out/f"{name}_feature_importance.csv",index=False)
        fpr,tpr,_=roc_curve(s.test.is_fraud,p); prec,rec,_=precision_recall_curve(s.test.is_fraud,p)
        curves += [{"model":name,"curve":"ROC","x":x,"y":y} for x,y in zip(fpr,tpr)] + [{"model":name,"curve":"PR","x":x,"y":y} for x,y in zip(rec,prec)]
    (out/"evaluation_metrics.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    pd.DataFrame(curves).to_csv(dash/"model_curves.csv",index=False)
    print(json.dumps(summary,indent=2)); print("So what? PR-AUC and recall reveal rare-event utility that headline accuracy would conceal.")
    return summary
if __name__=="__main__": run()
