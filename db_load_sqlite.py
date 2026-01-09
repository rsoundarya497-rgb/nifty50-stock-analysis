import sqlite3
import pandas as pd
from pathlib import Path

# ---- CONFIG ----
CSV_FILE = "clean_nifty50_stock_data.csv"
DB_FILE = "nifty50.db"
TABLE_NAME = "stocks"

def main():
    # 1) Check CSV exists
    if not Path(CSV_FILE).exists():
        raise FileNotFoundError(f"CSV not found: {CSV_FILE} (keep it in the same folder as this script)")

    # 2) Read CSV
    df = pd.read_csv(CSV_FILE)

    # 3) Basic cleanup (safe)
    df.columns = [c.strip().lower() for c in df.columns]

    # Ensure date is ISO text (SQLite-friendly)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)

    # 4) Create DB + write table
    conn = sqlite3.connect(DB_FILE)

    # Replace table each time for clean reload
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

    # 5) Create indexes (optional but nice)
    cur = conn.cursor()
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_symbol ON {TABLE_NAME}(symbol)")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_sector ON {TABLE_NAME}(sector)")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_date ON {TABLE_NAME}(date)")
    conn.commit()

    # 6) Verification queries
    print("✅ SQLite DB created & loaded successfully")
    print("DB file:", DB_FILE)
    print("Table:", TABLE_NAME)

    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    print("Total rows:", cur.fetchone()[0])

    cur.execute(f"SELECT COUNT(DISTINCT symbol) FROM {TABLE_NAME}")
    print("Distinct symbols:", cur.fetchone()[0])

    cur.execute(f"SELECT MIN(date), MAX(date) FROM {TABLE_NAME}")
    print("Date range:", cur.fetchone())

    cur.execute(f"SELECT symbol, date, close, volume FROM {TABLE_NAME} LIMIT 5")
    print("\nSample rows:")
    for row in cur.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
