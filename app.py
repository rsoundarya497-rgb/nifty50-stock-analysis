import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Nifty 50 Stock Analysis", layout="wide")

st.title("📈 Nifty 50 Stock Analysis Dashboard")

# Load data
df = pd.read_csv("clean_nifty50_stock_data.csv")

# Sidebar filters
st.sidebar.header("Filters")

sector = st.sidebar.multiselect(
    "Select Sector",
    options=df["sector"].unique(),
    default=df["sector"].unique()
)

symbol = st.sidebar.multiselect(
    "Select Symbol",
    options=df["symbol"].unique(),
    default=df["symbol"].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    [pd.to_datetime(df["date"]).min(), pd.to_datetime(df["date"]).max()]
)

# Apply filters
filtered_df = df[
    (df["sector"].isin(sector)) &
    (df["symbol"].isin(symbol)) &
    (pd.to_datetime(df["date"]).between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# KPIs
col1, col2 = st.columns(2)

col1.metric("Average Close Price", round(filtered_df["close"].mean(), 2))
col2.metric("Average Volume", int(filtered_df["volume"].mean()))

st.write("Total records:", len(filtered_df))

# Line chart
st.subheader("Close Price Trend")
st.line_chart(filtered_df, x="date", y="close")
