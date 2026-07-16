"""Shared time split and preprocessing for leakage-safe fraud models."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL = ["merchant_category", "ip_country"]
NUMERIC = ["log_amount", "transactions_per_hour", "transactions_per_day", "distinct_devices_7d", "distinct_ips_7d", "account_age_days", "transaction_hour", "day_of_week", "is_weekend", "is_night"]
FEATURES = CATEGORICAL + NUMERIC

@dataclass
class Splits:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame

def time_split(df: pd.DataFrame) -> Splits:
    ts = pd.to_datetime(df.timestamp, utc=True)
    train = df.loc[ts < "2025-10-01"].copy()
    validation = df.loc[(ts >= "2025-10-01") & (ts < "2025-11-01")].copy()
    test = df.loc[ts >= "2025-11-01"].copy()
    assert train.timestamp.max() < validation.timestamp.min() < test.timestamp.min()
    return Splits(train, validation, test)

def transformer(scale: bool = True) -> ColumnTransformer:
    return ColumnTransformer([("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL), ("numeric", StandardScaler() if scale else "passthrough", NUMERIC)], verbose_feature_names_out=False)

# So what? Chronological evaluation estimates how the policy handles future behavior and avoids optimistic leakage from random splitting.
