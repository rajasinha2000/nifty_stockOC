import time
import streamlit as st
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import schedule

# --- TELEGRAM CONFIG ---
BOT_TOKEN = "7735892458:AAELFRclang2MgJwO2Rd9RRwNmoll1LzlFg"
CHAT_ID = "5073531512"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)

# --- FETCH STOCKS FUNCTION ---
def fetch_stocks():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://intradayscreener.com/scan/26118/Raja_%285min_%2B_15min%29")
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

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
        print("⚠️ Could not fetch stock data:", e)
        return []

# --- STATE ---
if "last_stocks" not in st.session_state:
    st.session_state.last_stocks = []

# --- MAIN SCREEN ---
st.title("📈 Real-time Stock Screener Dashboard")

placeholder = st.empty()

def run_screener():
    current_time = datetime.now().strftime("%H:%M:%S")
    stocks = fetch_stocks()

    with placeholder.container():
        st.markdown(f"⏰ **Last checked:** {current_time}")
        if stocks:
            st.success(f"✅ Fetched {len(stocks)} stocks")
            for stock in stocks:
                st.markdown(f"- {stock}")
        else:
            st.warning("⚠️ No stock data found.")

    # Compare with last state
    new_stocks = [s for s in stocks if s not in st.session_state.last_stocks]

    if new_stocks:
        now = datetime.now().strftime("%H:%M:%S")
        message = f"📈 *New Stocks at {now}*\n\n" + "\n".join([f"🔸 {s}" for s in new_stocks])
        send_telegram_message(message)
        st.balloons()

    st.session_state.last_stocks = stocks

# --- REFRESH LOOP (every 5 minutes) ---
run_screener()
st_autorefresh = st.experimental_rerun
