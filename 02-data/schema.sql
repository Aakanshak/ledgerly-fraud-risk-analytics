PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS transactions (
  transaction_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  amount REAL NOT NULL CHECK (amount > 0),
  merchant_category TEXT NOT NULL,
  device_id TEXT NOT NULL,
  ip_country TEXT NOT NULL,
  is_fraud INTEGER NOT NULL CHECK (is_fraud IN (0, 1))
);

CREATE TABLE IF NOT EXISTS user_velocity_features (
  transaction_id TEXT PRIMARY KEY REFERENCES transactions(transaction_id),
  transactions_per_hour INTEGER NOT NULL,
  transactions_per_day INTEGER NOT NULL,
  distinct_devices_7d INTEGER NOT NULL,
  distinct_ips_7d INTEGER NOT NULL,
  account_age_days INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS chargebacks (
  transaction_id TEXT PRIMARY KEY REFERENCES transactions(transaction_id),
  chargeback_date TEXT NOT NULL,
  resolution_cost REAL NOT NULL CHECK (resolution_cost >= 0)
);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_segment ON transactions(merchant_category, ip_country);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);

-- So what? Constraints and indexes make the local analytical source reproducible and keep common risk slices responsive.
