WITH segmented AS (
  SELECT merchant_category, ip_country,
    CASE WHEN amount < 25 THEN '<$25'
         WHEN amount < 100 THEN '$25-$99'
         WHEN amount < 250 THEN '$100-$249'
         ELSE '$250+' END AS amount_bucket,
    amount, is_fraud
  FROM transactions
)
SELECT merchant_category, ip_country, amount_bucket,
  COUNT(*) AS transactions, SUM(is_fraud) AS fraud_transactions,
  ROUND(AVG(is_fraud), 5) AS fraud_rate,
  ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) AS fraud_amount
FROM segmented
GROUP BY 1, 2, 3
HAVING COUNT(*) >= 100
ORDER BY fraud_rate DESC;

-- So what? Concentration identifies where targeted controls can outperform a blunt platform-wide decline rule.
