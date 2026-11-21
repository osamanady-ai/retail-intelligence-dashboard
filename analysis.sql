-- SQLite query executed by main.py against the cleaned in-memory table.
SELECT Country, SUM(net_value_gbp) AS net_sales_gbp
FROM retail
GROUP BY Country
ORDER BY net_sales_gbp DESC;
