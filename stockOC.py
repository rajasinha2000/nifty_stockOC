import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="📈 Real-time Stock Screener", layout="centered")
st.title("📈 Real-time Stock Screener Dashboard")
st.markdown("This app checks for stocks every 5 minutes from Intraday Screener.")

# Store previous stock list
if "previous_stocks" not in st.session_state:
    st.session_state.previous_stocks = []

def fetch_stocks():
    url = "https://intradayscreener.com/scan/26118/Raja_%285min_%2B_15min%29"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if not table:
            return []

        stocks = []
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if cols:
                stocks.append(cols[0].text.strip())
        return stocks

    except Exception as e:
        st.error(f"❌ Error fetching stocks: {e}")
        return []

def run_screener():
    st.info("⏳ Checking stocks...")
    stocks = fetch_stocks()

    if stocks:
        new_stocks = [stock for stock in stocks if stock not in st.session_state.previous_stocks]
        st.session_state.previous_stocks = stocks

        if new_stocks:
            st.success(f"📈 *New Stocks at {time.strftime('%H:%M:%S')}*")
            for stock in new_stocks:
                st.markdown(f"🔸 {stock}")
        else:
            st.warning("🔁 No new stocks found.")
    else:
        st.error("⚠️ Could not fetch stock data.")

# Button to trigger check manually
if st.button("🔍 Start Screener Now"):
    run_screener()

# Auto-refresh every 5 minutes (client side)
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)
st.caption("🔄 This page refreshes every 5 minutes.")
