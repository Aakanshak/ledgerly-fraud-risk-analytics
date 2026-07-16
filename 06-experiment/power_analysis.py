"""Approximate two-proportion sample size and experiment duration."""
from __future__ import annotations
import json
from pathlib import Path
from statistics import NormalDist
import math

def sample_size_per_group(baseline_rate=.0307, relative_reduction=.15, alpha=.05, power=.80):
    p1=baseline_rate; p2=p1*(1-relative_reduction); pbar=(p1+p2)/2
    za=NormalDist().inv_cdf(1-alpha/2); zb=NormalDist().inv_cdf(power)
    n=((za*math.sqrt(2*pbar*(1-pbar))+zb*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2)/(p1-p2)**2
    return math.ceil(n)

def run(daily_eligible_traffic=5500, test_share=.20):
    n=sample_size_per_group(); daily_smallest=daily_eligible_traffic*min(test_share,1-test_share)
    result={"sample_size_per_group":n,"total_balanced_sample":2*n,"assumed_baseline_fraud_rate":.0307,"minimum_detectable_relative_reduction":.15,"alpha":.05,"power":.80,"estimated_days_at_20pct_test":math.ceil(n/daily_smallest),"recommended_duration_days":28}
    out=Path(__file__).parent/"outputs"; out.mkdir(exist_ok=True); (out/"power_analysis.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2)); print("So what? A four-week test balances statistical sensitivity with enough time to observe weekday mix and delayed operational signals.")
    return result
if __name__=="__main__": run()
