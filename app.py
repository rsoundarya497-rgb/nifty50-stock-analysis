import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Nifty 50 Stock Analysis", layout="wide")
st.title("📈 Nifty 50 Stock Analysis Dashboard")
st.caption("Interactive dashboard using cleaned Nifty 50 OHLCV data.")

# ---------------------------
# LOAD DATA (safe)
# ---------------------------
DATA_FILE = "clean_nifty50_stock_data.csv"

try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    st.error(
        f"❌ File not found: {DATA_FILE}\n\n"
        "✅ Fix:\n"
        "1) Put clean_nifty50_stock_data.csv in the SAME folder as app.py\n"
        "2) Run: streamlit run app.py from that folder"
    )
    st.stop()

# Basic cleaning
required_cols = {"symbol", "sector", "COMPANY", "date", "open", "high", "low", "close", "volume"}
missing_cols = required_cols - set(df.columns)
if missing_cols:
    st.error(f"❌ Missing columns in CSV: {missing_cols}")
    st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"]).copy()
df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("🔎 Filters")

all_sectors = sorted(df["sector"].dropna().unique().tolist())
all_symbols = sorted(df["symbol"].dropna().unique().tolist())

sector_sel = st.sidebar.multiselect("Select Sector", options=all_sectors, default=all_sectors)
symbol_sel = st.sidebar.multiselect("Select Symbol", options=all_symbols, default=all_symbols)

min_d = df["date"].min().date()
max_d = df["date"].max().date()

date_range = st.sidebar.date_input("Select Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

# date_input can sometimes return a single date; normalize to (start,end)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date = pd.to_datetime(date_range)
    end_date = pd.to_datetime(date_range)

# Apply filters
filtered_df = df[
    (df["sector"].isin(sector_sel)) &
    (df["symbol"].isin(symbol_sel)) &
    (df["date"].between(start_date, end_date))
].copy()

if filtered_df.empty:
    st.warning("No data for the selected filters. Try expanding sector/symbol/date range.")
    st.stop()

# ---------------------------
# KPIs
# ---------------------------
col1, col2, col3 = st.columns(3)

avg_close = filtered_df["close"].mean()
avg_vol = filtered_df["volume"].mean()
total_rows = len(filtered_df)

col1.metric("Average Close Price", f"{avg_close:,.2f}")
col2.metric("Average Volume", f"{avg_vol:,.0f}")
col3.metric("Total Records", f"{total_rows:,}")

# ---------------------------
# CALCULATIONS (returns, volatility, yearly return)
# ---------------------------
# Daily return per symbol
filtered_df["prev_close"] = filtered_df.groupby("symbol")["close"].shift(1)
filtered_df["daily_return"] = (filtered_df["close"] - filtered_df["prev_close"]) / filtered_df["prev_close"]
filtered_df["daily_return"] = filtered_df["daily_return"].replace([np.inf, -np.inf], np.nan)

# Volatility = std dev of daily returns per symbol
vol_df = (
    filtered_df.dropna(subset=["daily_return"])
    .groupby("symbol")["daily_return"]
    .std()
    .reset_index(name="volatility")
    .sort_values("volatility", ascending=False)
)

# Yearly return per symbol within filtered range:
# (last close - first close) / first close
first_close = filtered_df.groupby("symbol")["close"].first()
last_close = filtered_df.groupby("symbol")["close"].last()
yr_return = ((last_close - first_close) / first_close).reset_index(name="yearly_return")
yr_return = yr_return.sort_values("yearly_return", ascending=False)

top10_gainers = yr_return.head(10)
top10_losers = yr_return.tail(10).sort_values("yearly_return", ascending=True)

# Sector-wise average yearly return
sector_perf = (
    yr_return.merge(filtered_df[["symbol", "sector"]].drop_duplicates(), on="symbol", how="left")
    .groupby("sector")["yearly_return"]
    .mean()
    .reset_index()
    .sort_values("yearly_return", ascending=False)
)

# ---------------------------
# TABS (clean structure)
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trend", "⚡ Performance", "🧠 Risk & Correlation"])

# ---------------------------
# TAB 1: OVERVIEW
# ---------------------------
with tab1:
    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(50), use_container_width=True)

    st.subheader("Green vs Red Stocks (based on Yearly Return in selected date range)")
    green = (yr_return["yearly_return"] > 0).sum()
    red = (yr_return["yearly_return"] <= 0).sum()
    st.write(f"✅ Green stocks: **{green}**")
    st.write(f"🔴 Red stocks: **{red}**")

# ---------------------------
# TAB 2: TREND
# ---------------------------
with tab2:
    st.subheader("Close Price Trend")

    # For a readable line chart, pivot close prices
    pivot_close = filtered_df.pivot_table(index="date", columns="symbol", values="close", aggfunc="mean").sort_index()

    st.line_chart(pivot_close)

    st.caption("Tip: Select 1–3 symbols in the sidebar for a cleaner trend view.")

# ---------------------------
# TAB 3: PERFORMANCE
# ---------------------------
with tab3:
    st.subheader("Top 10 Gainers & Losers (Yearly Return)")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🟢 Top 10 Gainers")
        st.dataframe(top10_gainers, use_container_width=True)

        fig = plt.figure()
        plt.bar(top10_gainers["symbol"], top10_gainers["yearly_return"])
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Yearly Return")
        plt.title("Top 10 Gainers")
        st.pyplot(fig)

    with c2:
        st.markdown("### 🔴 Top 10 Losers")
        st.dataframe(top10_losers, use_container_width=True)

        fig = plt.figure()
        plt.bar(top10_losers["symbol"], top10_losers["yearly_return"])
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Yearly Return")
        plt.title("Top 10 Losers")
        st.pyplot(fig)

    st.subheader("Sector-wise Average Yearly Return")
    st.dataframe(sector_perf, use_container_width=True)

    fig = plt.figure()
    plt.bar(sector_perf["sector"], sector_perf["yearly_return"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Avg Yearly Return")
    plt.title("Sector-wise Average Yearly Return")
    st.pyplot(fig)

# ---------------------------
# TAB 4: RISK & CORRELATION
# ---------------------------
with tab4:
    st.subheader("Top 10 Most Volatile Stocks (Risk Insight)")
    top10_vol = vol_df.head(10).copy()
    st.dataframe(top10_vol, use_container_width=True)

    fig = plt.figure()
    plt.bar(top10_vol["symbol"], top10_vol["volatility"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Volatility (Std Dev of Daily Returns)")
    plt.title("Top 10 Most Volatile Stocks")
    st.pyplot(fig)

    st.subheader("Correlation Heatmap (Close Prices)")

    # Correlation based on close price pivot
    corr = pivot_close.corr()

    fig = plt.figure(figsize=(10, 6))
    plt.imshow(corr, aspect="auto")
    plt.colorbar()
    plt.title("Stock Close Price Correlation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    st.pyplot(fig)

st.success("✅ Dashboard loaded successfully.")
