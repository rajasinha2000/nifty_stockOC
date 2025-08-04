import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from streamlit_autorefresh import st_autorefresh

# 🔧 Telegram credentials
BOT_TOKEN = "7735892458:AAELFRclang2MgJwO2Rd9RRwNmoll1LzlFg"
CHAT_ID = "5073531512"

# 🧠 Cache the previously sent stocks
st.set_page_config(page_title="📈 Stock Screener", layout="wide")
st.title("📈 Real-time Stock Screener Dashboard")

# Auto-refresh every 5 minutes (300000 ms)
st_autorefresh(interval=300000, key="auto-refresh")

# 🔁 Store previously fetched stocks to compare
if "prev_stocks" not in st.session_state:
    st.session_state.prev_stocks = []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        st.warning(f"Telegram error: {e}")

def fetch_stocks():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.niftytrader.in/option-chain"
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", {"id": "stocksInNews"})

        if not table:
            st.warning("⚠️ Could not fetch stock data.")
            return []

        rows = table.find_all("tr")[1:]  # skip header
        stocks = [row.find_all("td")[1].text.strip() for row in rows if row.find_all("td")]
        return stocks

    except Exception as e:
        st.error(f"❌ Error fetching stocks: {e}")
        return []
    finally:
        driver.quit()

def run_screener():
    stocks = fetch_stocks()

    if not stocks:
        st.warning("⚠️ No stocks found.")
        return

    # 🆕 Compare with previous
    new_stocks = [s for s in stocks if s not in st.session_state.prev_stocks]

    if new_stocks:
        st.subheader(f"📈 *New Stocks at {time.strftime('%H:%M:%S')}*")
        for s in new_stocks:
            st.markdown(f"🔸 **{s}**")
        message = f"📈 *New Stocks at {time.strftime('%H:%M:%S')}*\n\n" + "\n".join(f"🔸 {s}" for s in new_stocks)
        send_telegram_message(message)
    else:
        st.info("✅ No new stocks detected.")

    # 💾 Update state
    st.session_state.prev_stocks = stocks

# 🚀 Run
run_screener()
