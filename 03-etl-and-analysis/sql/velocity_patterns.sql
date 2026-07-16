WITH buckets AS (
  SELECT t.is_fraud,
    CASE WHEN v.transactions_per_hour = 1 THEN '1'
         WHEN v.transactions_per_hour <= 3 THEN '2-3'
         WHEN v.transactions_per_hour <= 6 THEN '4-6' ELSE '7+' END AS hourly_velocity,
    CASE WHEN v.distinct_devices_7d = 1 THEN '1'
         WHEN v.distinct_devices_7d = 2 THEN '2' ELSE '3+' END AS device_count
  FROM transactions t JOIN user_velocity_features v USING(transaction_id)
)
SELECT hourly_velocity, device_count, COUNT(*) AS transactions,
  SUM(is_fraud) AS fraud_transactions, ROUND(AVG(is_fraud), 5) AS fraud_rate
FROM buckets GROUP BY 1, 2 ORDER BY fraud_rate DESC;

-- So what? Velocity raises risk but legitimate power users create overlap, so velocity should inform a score rather than act as a standalone block rule.
