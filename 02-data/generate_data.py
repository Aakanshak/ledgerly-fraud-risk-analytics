"""Generate reproducible, realistically overlapping synthetic Ledgerly data."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
N_TRANSACTIONS = 200_000
START = pd.Timestamp("2025-01-01", tz="UTC")
END = pd.Timestamp("2025-12-31 23:59:59", tz="UTC")

CATEGORIES = np.array(["grocery", "electronics", "travel", "digital_goods", "gaming", "fashion", "fuel", "restaurants"])
CATEGORY_P = np.array([.20, .10, .08, .12, .08, .12, .10, .20])
COUNTRIES = np.array(["US", "GB", "CA", "DE", "IN", "BR", "NG", "RU"])
COUNTRY_P = np.array([.50, .10, .08, .07, .10, .07, .04, .04])


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def generate(n: int = N_TRANSACTIONS, seed: int = SEED) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    Faker.seed(seed)
    n_users = max(20_000, n // 4)
    user_ids = np.array([f"usr_{i:07d}" for i in range(n_users)])
    user_weight = rng.lognormal(0, .85, n_users)
    user_weight /= user_weight.sum()
    user_idx = rng.choice(n_users, n, p=user_weight)

    total_seconds = int((END - START).total_seconds())
    seconds = np.sort(rng.integers(0, total_seconds, n))
    timestamp = START + pd.to_timedelta(seconds, unit="s")
    month = timestamp.month.to_numpy()
    category = rng.choice(CATEGORIES, n, p=CATEGORY_P)
    country = rng.choice(COUNTRIES, n, p=COUNTRY_P)

    amount_mu = np.select(
        [category == "travel", category == "electronics", category == "grocery", category == "fuel"],
        [5.0, 4.7, 3.5, 3.7], default=3.9,
    )
    amount = np.clip(rng.lognormal(amount_mu, .75), 2, 5000).round(2)

    account_age_days = np.maximum(0, rng.gamma(3.2, 105, n).astype(int))
    legitimate_power_user = rng.random(n_users) < .075
    power = legitimate_power_user[user_idx]
    tx_per_hour = np.maximum(1, rng.poisson(0.45 + power * 2.2, n) + 1)
    spike = rng.random(n) < .035
    tx_per_hour += spike * rng.poisson(5.0, n)
    tx_per_day = tx_per_hour + rng.poisson(2.2 + power * 7.5, n)
    distinct_devices = 1 + rng.binomial(4, .04 + .10 * spike + .05 * power, n)
    distinct_ips = 1 + rng.binomial(5, .05 + .13 * spike + .05 * power, n)

    cat_risk = pd.Series(category).map({"digital_goods": .65, "gaming": .55, "electronics": .45, "travel": .25}).fillna(0).to_numpy()
    geo_risk = pd.Series(country).map({"NG": .85, "RU": .75, "BR": .28}).fillna(0).to_numpy()
    interaction = ((np.isin(category, ["digital_goods", "gaming"])) & np.isin(country, ["NG", "RU", "BR"])).astype(float)
    night = ((timestamp.hour.to_numpy() < 5) | (timestamp.hour.to_numpy() > 23)).astype(float)
    trend = (month - 1) / 11
    latent = (
        -5.35 + cat_risk + geo_risk + .75 * interaction + .34 * np.log1p(tx_per_hour)
        + .20 * np.log1p(tx_per_day) + .22 * (distinct_devices - 1) + .18 * (distinct_ips - 1)
        + .30 * (account_age_days < 21) + .17 * np.log1p(amount / 100) + .16 * night + .30 * trend
        - .28 * power + rng.normal(0, .85, n)
    )
    fraud_probability = sigmoid(latent)
    is_fraud = rng.binomial(1, fraud_probability)

    device_base = rng.integers(0, max(15_000, n_users // 2), n)
    ip_base = rng.integers(1, 255, (n, 3))
    transactions = pd.DataFrame({
        "transaction_id": [f"txn_{i:09d}" for i in range(n)],
        "user_id": user_ids[user_idx],
        "timestamp": timestamp.astype(str),
        "amount": amount,
        "merchant_category": category,
        "device_id": [f"dev_{x:07d}" for x in device_base],
        "ip_country": country,
        "is_fraud": is_fraud.astype(int),
    })
    velocity = pd.DataFrame({
        "transaction_id": transactions["transaction_id"],
        "transactions_per_hour": tx_per_hour.astype(int),
        "transactions_per_day": tx_per_day.astype(int),
        "distinct_devices_7d": distinct_devices.astype(int),
        "distinct_ips_7d": distinct_ips.astype(int),
        "account_age_days": account_age_days.astype(int),
    })
    fraud_tx = transactions.loc[transactions.is_fraud.eq(1), ["transaction_id", "timestamp", "amount"]].copy()
    fraud_time = pd.to_datetime(fraud_tx.pop("timestamp"), utc=True)
    chargebacks = pd.DataFrame({
        "transaction_id": fraud_tx["transaction_id"].to_numpy(),
        "chargeback_date": (fraud_time + pd.to_timedelta(rng.integers(7, 61, len(fraud_tx)), unit="D")).astype(str),
        "resolution_cost": np.round(rng.gamma(2.0, 6.0, len(fraud_tx)) + 5, 2),
    })
    return transactions, velocity, chargebacks


def quality_report(transactions: pd.DataFrame, velocity: pd.DataFrame) -> dict:
    y = transactions["is_fraud"]
    joined = transactions.join(velocity.drop(columns="transaction_id"))
    return {
        "transactions": int(len(joined)),
        "users": int(joined.user_id.nunique()),
        "fraud_count": int(y.sum()),
        "fraud_rate": float(y.mean()),
        "legitimate_accuracy_baseline": float(1 - y.mean()),
        "fraud_median_tx_per_hour": float(joined.loc[y.eq(1), "transactions_per_hour"].median()),
        "legit_median_tx_per_hour": float(joined.loc[y.eq(0), "transactions_per_hour"].median()),
        "fraud_median_amount": float(joined.loc[y.eq(1), "amount"].median()),
        "legit_median_amount": float(joined.loc[y.eq(0), "amount"].median()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=N_TRANSACTIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "generated")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tx, velocity, chargebacks = generate(args.rows, args.seed)
    tx.to_csv(args.output_dir / "transactions.csv", index=False)
    velocity.to_csv(args.output_dir / "user_velocity_features.csv", index=False)
    chargebacks.to_csv(args.output_dir / "chargebacks.csv", index=False)
    pd.Series(quality_report(tx, velocity)).to_json(args.output_dir / "data_quality_report.json", indent=2)
    print(pd.Series(quality_report(tx, velocity)).to_string())
    print("\nSo what? Rare fraud overlaps legitimate high-velocity behavior, making ranking and cost-sensitive decisions necessary.")


if __name__ == "__main__":
    main()
