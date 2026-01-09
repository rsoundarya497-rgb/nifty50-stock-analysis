import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty50.db")

query = """
SELECT symbol, ROUND(AVG(close),2) AS avg_close
FROM stocks
GROUP BY symbol
ORDER BY avg_close DESC
LIMIT 5;
"""

df = pd.read_sql_query(query, conn)
print(df)

conn.close()
