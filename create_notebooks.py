"""Create concise, executable analysis notebooks with business interpretations."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parent
def build(path,title,cells):
    nb=nbf.v4.new_notebook(); nb["cells"]=[nbf.v4.new_markdown_cell(f"# {title}\n\nRun from the repository root after `python run_pipeline.py`.")]
    for kind,content in cells: nb["cells"].append(nbf.v4.new_code_cell(content) if kind=="code" else nbf.v4.new_markdown_cell(content))
    nb["metadata"]["kernelspec"]={"display_name":"Python 3","language":"python","name":"python3"}
    path.parent.mkdir(parents=True,exist_ok=True); nbf.write(nb,path)

build(ROOT/"03-etl-and-analysis/python/eda_notebook.ipynb","Ledgerly EDA",[
    ("code","import pandas as pd\nimport plotly.express as px\ndf=pd.read_parquet('03-etl-and-analysis/outputs/model_features.parquet')\nprint(df.shape, df.is_fraud.mean())"),
    ("code","monthly=df.groupby('month').agg(transactions=('transaction_id','size'),fraud_rate=('is_fraud','mean')).reset_index()\npx.line(monthly,x='month',y='fraud_rate',markers=True,title='Monthly fraud rate')"),
    ("code","heat=df.pivot_table(index='merchant_category',columns='ip_country',values='is_fraud',aggfunc='mean')\npx.imshow(heat,text_auto='.1%',aspect='auto',color_continuous_scale='RdYlGn_r',title='Fraud rate by category and geography')"),
    ("md","## So what?\n\nFraud is rare but concentrated, and risky velocity overlaps legitimate power use. Segment-aware scoring is preferable to single-feature blanket rules.")])
build(ROOT/"04-modeling/model_evaluation.ipynb","Fraud model evaluation",[
    ("code","import json, pandas as pd\nfrom pathlib import Path\nm=json.loads(Path('04-modeling/artifacts/evaluation_metrics.json').read_text())\npd.DataFrame(m['models']).T"),
    ("code","import plotly.express as px\nc=pd.read_csv('08-dashboard/app_data/model_curves.csv')\npx.line(c,x='x',y='y',color='model',facet_col='curve',title='Out-of-time model curves')"),
    ("md","## Calibration and imbalance\n\nAccuracy is misleading: predicting every transaction as legitimate is over 97% accurate yet catches no fraud. ROC-AUC, PR-AUC, precision, recall, calibration, and dollar cost are evaluated on the final two months after training on earlier months."),
    ("md","## So what?\n\nThe chosen model is the one that supports lower out-of-time decision cost; model metrics are diagnostics, not the final operating objective.")])
build(ROOT/"05-cost-based-decisioning/threshold_analysis.ipynb","Cost-based threshold analysis",[
    ("code","import pandas as pd, plotly.express as px\nc=pd.read_csv('05-cost-based-decisioning/outputs/threshold_cost_curve.csv')\npx.line(c,x='threshold',y=['fraud_dollars_blocked','legitimate_customer_cost','total_cost'],title='Dollar tradeoff across thresholds')"),
    ("code","c.loc[c.total_cost.idxmin()]"),
    ("md","## So what?\n\nThe threshold is an economic policy choice. Lowering it blocks additional fraud but spends customer goodwill and support dollars; the selected point minimizes combined cost within the false-decline guardrail.")])
build(ROOT/"06-experiment/experiment_analysis.ipynb","Threshold experiment analysis",[
    ("code","import json, pandas as pd\nfrom pathlib import Path\ns=pd.read_csv('06-experiment/outputs/experiment_summary.csv'); display(s)\njson.loads(Path('06-experiment/outputs/experiment_results.json').read_text())"),
    ("code","import plotly.express as px\npx.bar(s,x='group',y='fraud_loss_per_transaction',color='group',title='Fraud loss per transaction')"),
    ("md","## So what?\n\nThe experiment converts an offline threshold recommendation into causal evidence and checks whether lower fraud loss is worth the observed false-decline increase.")])
print("Created four notebooks")
