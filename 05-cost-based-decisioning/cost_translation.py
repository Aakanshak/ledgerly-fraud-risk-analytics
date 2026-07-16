"""Translate fraud scores and errors into auditable dollar costs."""
from __future__ import annotations
import numpy as np, pandas as pd

LOST_MARGIN_RATE=.029
SUPPORT_COST=8.0
CHARGEBACK_FEE=15.0

def evaluate_thresholds(predictions: pd.DataFrame, thresholds=np.linspace(.001,.30,300)) -> pd.DataFrame:
    rows=[]; y=predictions.is_fraud.to_numpy(bool); amount=predictions.amount.to_numpy(float); score=predictions.score.to_numpy(float)
    fp_unit=SUPPORT_COST + LOST_MARGIN_RATE*amount
    fn_unit=amount + CHARGEBACK_FEE + predictions.resolution_cost.to_numpy(float)
    fraud_exposure=fn_unit[y].sum()
    for threshold in thresholds:
        block=score>=threshold; fp=block & ~y; fn=~block & y; tp=block & y
        fp_cost=fp_unit[fp].sum(); fn_cost=fn_unit[fn].sum(); total=fp_cost+fn_cost
        rows.append({"threshold":threshold,"blocked_transactions":int(block.sum()),"true_positives":int(tp.sum()),"false_positives":int(fp.sum()),"false_negatives":int(fn.sum()),"precision":tp.sum()/max(block.sum(),1),"recall":tp.sum()/max(y.sum(),1),"false_decline_rate":fp.sum()/max((~y).sum(),1),"fraud_dollars_blocked":fraud_exposure-fn_cost,"legitimate_customer_cost":fp_cost,"residual_fraud_loss":fn_cost,"total_cost":total})
    return pd.DataFrame(rows)

# So what? A false decline is not equivalent to a missed $1,000 fraud event; dollar translation makes the threshold reflect economic asymmetry.
