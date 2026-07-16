"""Ledgerly executive fraud-risk decision dashboard."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

HERE=Path(__file__).resolve().parent; DATA=HERE/"app_data"
st.set_page_config(page_title="Ledgerly Risk Decision Lab",page_icon="🛡️",layout="wide")
st.markdown("""<style>.block-container{padding-top:2rem}.metric-card{background:#101d2f;border:1px solid #263a52;border-radius:12px;padding:16px}.stApp{background:#07111f;color:#f4f7fb}</style>""",unsafe_allow_html=True)
st.title("Ledgerly Risk Decision Lab")
st.caption("Turn fraud probabilities into an auditable dollar decision • synthetic portfolio data")

@st.cache_data
def load():
    return (pd.read_csv(DATA/"fraud_rate_trend.csv"),pd.read_csv(DATA/"risk_heatmap.csv"),pd.read_csv(DATA/"model_curves.csv"),pd.read_csv(DATA/"threshold_cost_curve.csv"),pd.read_csv(DATA/"experiment_summary.csv"),json.loads((DATA/"optimal_threshold.json").read_text()))
trend,heat,curves,cost,experiment,opt=load()

c1,c2,c3,c4=st.columns(4)
c1.metric("Recommended threshold",f"{opt['optimal_threshold']:.3f}",f"vs {opt['current_threshold']:.2f} baseline")
c2.metric("Annualized savings",f"${opt['annualized_savings']:,.0f}")
c3.metric("Fraud recall",f"{opt['optimal_recall']:.1%}")
c4.metric("False-decline rate",f"{opt['optimal_false_decline_rate']:.2%}","2.0% guardrail")

tab1,tab2,tab3,tab4=st.tabs(["Decision simulator","Risk concentration","Model performance","Experiment"])
with tab1:
    st.subheader("Cost-based threshold simulator")
    threshold=st.slider("Decision threshold — lower blocks more transactions",float(cost.threshold.min()),float(cost.threshold.max()),float(opt["optimal_threshold"]),.001,format="%.3f")
    row=cost.iloc[(cost.threshold-threshold).abs().argsort()[:1]].iloc[0]
    a,b,c,d=st.columns(4)
    a.metric("Fraud $ blocked",f"${row.fraud_dollars_blocked:,.0f}")
    b.metric("Legitimate customer cost",f"${row.legitimate_customer_cost:,.0f}")
    c.metric("Residual fraud loss",f"${row.residual_fraud_loss:,.0f}")
    d.metric("Total decision cost",f"${row.total_cost:,.0f}")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=cost.threshold,y=cost.fraud_dollars_blocked,name="Fraud $ blocked",line=dict(color="#2dd4bf",width=3)))
    fig.add_trace(go.Scatter(x=cost.threshold,y=cost.legitimate_customer_cost,name="Legitimate customer cost",line=dict(color="#fb7185",width=3)))
    fig.add_trace(go.Scatter(x=cost.threshold,y=cost.total_cost,name="Total cost",yaxis="y2",line=dict(color="#fbbf24",dash="dot")))
    fig.add_vline(x=threshold,line_color="white",annotation_text=f"Selected {threshold:.3f}")
    fig.update_layout(template="plotly_dark",height=480,xaxis_title="Threshold",yaxis_title="Tradeoff dollars",yaxis2=dict(title="Total cost",overlaying="y",side="right"),legend=dict(orientation="h"))
    st.plotly_chart(fig,width="stretch")
    st.info("So what? Drag the threshold: fraud blocked rises as the threshold falls, but so does the cost imposed on legitimate customers. The recommendation minimizes their combined cost within the CX guardrail.")
with tab2:
    left,right=st.columns([1,1])
    with left:
        fig=px.line(trend,x="month",y="fraud_rate",markers=True,title="Fraud rate over time"); fig.update_yaxes(tickformat=".1%"); fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig,width="stretch")
    with right:
        h=heat.set_index("merchant_category"); fig=px.imshow(h,text_auto=".1%",aspect="auto",color_continuous_scale="RdYlGn_r",title="Fraud rate: category × geography")
        fig.update_layout(template="plotly_dark"); st.plotly_chart(fig,width="stretch")
    st.info("So what? Concentrated routes support targeted step-up controls instead of indiscriminate platform-wide blocking.")
with tab3:
    model=st.radio("Model",["gradient_boosting","logistic_regression"],horizontal=True)
    left,right=st.columns(2)
    for container,kind,title in [(left,"ROC","ROC curve"),(right,"PR","Precision–recall curve")]:
        d=curves[(curves.model==model)&(curves.curve==kind)]; fig=px.line(d,x="x",y="y",title=title); fig.update_layout(template="plotly_dark"); container.plotly_chart(fig,width="stretch")
    st.info("So what? PR performance is emphasized because 97%+ accuracy is achievable by predicting no fraud and would provide zero protection.")
with tab4:
    st.dataframe(experiment.style.format({"fraud_loss":"${:,.0f}","fraud_loss_per_transaction":"${:.2f}","false_decline_rate":"{:.2%}"}),width="stretch",hide_index=True)
    fig=px.bar(experiment,x="group",y="fraud_loss_per_transaction",color="group",title="Fraud loss per transaction: test vs control",text_auto="$.2f"); fig.update_layout(template="plotly_dark",showlegend=False)
    st.plotly_chart(fig,width="stretch")
    st.info("So what? The simulated holdout reduces fraud loss per transaction while making the incremental false-decline tradeoff measurable before rollout.")

st.caption("Synthetic data • Pretrained models • No external database • Costs: 2.9% lost margin + $8 support per false decline; fraud amount + $15 fee + resolution cost per miss")
