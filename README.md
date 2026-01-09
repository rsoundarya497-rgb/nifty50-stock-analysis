## Data Source
- Raw stock market data is provided in **YAML format**, organized month-wise.
- Each month folder contains date-wise YAML files for Nifty 50 stocks.

## Data Extraction & Cleaning (Python)
- A Python script (`yaml_to_csv.py`) is used to:
  - Read raw YAML files
  - Normalize column names
  - Handle missing values
  - Convert date formats
- The cleaned data is converted into a single CSV file and per-symbol CSV files.

## Database Interaction
- The cleaned CSV data is stored in a **SQLite database** using Python.
- Script used: `db_load_sqlite.py`
- The script:
  - Creates a SQLite database (`nifty50.db`)
  - Inserts all stock records into a table
  - Executes SQL queries to validate row count, symbols, and date range

## Data Analysis
- Python is used to calculate:
  - Daily returns
  - Volatility (standard deviation of returns)
  - Top gainers and losers
  - Sector-wise performance
  - Correlation between stock prices

## Project Workflow
1. Raw YAML stock data is collected.
2. Python scripts clean and convert YAML data into CSV.
3. Cleaned data is stored in a SQLite database.
4. Data is analyzed using Python.
5. Insights are visualized using Streamlit and Power BI dashboards.

## Tools Used
- Python
- Pandas
- Streamlit
- Power BI
- SQLite
- Matplotlib
- PyYAML


## How to Execute the Project (End-to-End)

### Step 1: YAML to CSV Conversion
Convert raw YAML data into a cleaned CSV file:
```bash
python yaml_to_csv.py

