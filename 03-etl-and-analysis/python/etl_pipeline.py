"""Build clean point-in-time features and SQL/dashboard aggregates."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "02-data" / "ledgerly.db"
OUT = ROOT / "03-etl-and-analysis" / "outputs"
DASH = ROOT / "08-dashboard" / "app_data"

def run() -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True); DASH.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as conn:
        df = pd.read_sql_query("""SELECT t.*, v.transactions_per_hour, v.transactions_per_day,
          v.distinct_devices_7d, v.distinct_ips_7d, v.account_age_days,
          COALESCE(c.resolution_cost, 0) AS resolution_cost
          FROM transactions t JOIN user_velocity_features v USING(transaction_id)
          LEFT JOIN chargebacks c USING(transaction_id)""", conn, parse_dates=["timestamp"])
        for sql_name, output_name in [("fraud_rate_trend.sql","fraud_rate_trend.csv"),("fraud_by_segment.sql","fraud_by_segment.csv"),("velocity_patterns.sql","velocity_patterns.csv")]:
            sql = (ROOT / "03-etl-and-analysis" / "sql" / sql_name).read_text(encoding="utf-8")
            pd.read_sql_query(sql, conn).to_csv(OUT / output_name, index=False)
    assert df.transaction_id.is_unique and df.is_fraud.isin([0,1]).all()
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True)
    df["transaction_hour"] = df.timestamp.dt.hour
    df["day_of_week"] = df.timestamp.dt.dayofweek
    df["is_weekend"] = (df.day_of_week >= 5).astype(int)
    df["is_night"] = ((df.transaction_hour < 5) | (df.transaction_hour >= 23)).astype(int)
    df["log_amount"] = np.log1p(df.amount)
    df["month"] = df.timestamp.dt.to_period("M").astype(str)
    df.to_parquet(OUT / "model_features.parquet", index=False)
    pd.read_csv(OUT / "fraud_rate_trend.csv").to_csv(DASH / "fraud_rate_trend.csv", index=False)
    heat = df.pivot_table(index="merchant_category", columns="ip_country", values="is_fraud", aggfunc="mean").reset_index()
    heat.to_csv(DASH / "risk_heatmap.csv", index=False)
    print({"rows":len(df),"columns":len(df.columns),"fraud_rate":round(df.is_fraud.mean(),4)})
    print("So what? The model table contains only transaction-time features; delayed chargeback cost is retained for evaluation, not prediction.")
    return df

if __name__ == "__main__": run()
