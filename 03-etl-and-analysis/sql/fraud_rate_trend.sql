SELECT
  strftime('%Y-%m', timestamp) AS month,
  COUNT(*) AS transactions,
  SUM(is_fraud) AS fraud_transactions,
  ROUND(AVG(is_fraud), 5) AS fraud_rate,
  ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) AS fraud_amount
FROM transactions
GROUP BY 1
ORDER BY 1;

-- So what? The monthly view distinguishes structural loss growth from isolated spikes and creates a drift-monitoring baseline.
