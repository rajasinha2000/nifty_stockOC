import streamlit as st
import time
import requests
import schedule
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Telegram Bot Config
BOT_TOKEN = "7735892458:AAELFRclang2MgJwO2Rd9RRwNmoll1LzlFg"
CHAT_ID = "5073531512"

st.set_page_config(page_title="📈 Real-time Stock Screener", layout="wide")
st.title("📈 Real-time Stock Screener Dashboard")

stocks_display = st.empty()

last_fetched = None
last_sent = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Telegram error: {e}")

def fetch_stocks():
    url = "https://intradayscreener.com/scan/26118/Raja_%285min_%2B_15min%29"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(5)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    stocks = []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if cols:
            stocks.append(cols[0].text.strip())
    return stocks

def run_screener():
    global last_fetched, last_sent

    stocks = fetch_stocks()
    current_time = datetime.now().strftime("%H:%M:%S")
    if stocks:
        new_stocks = [s for s in stocks if s not in last_sent]
        if new_stocks:
            message = f"*📈 New Stocks at {current_time}*\n\n" + "\n".join([f"🔸 {s}" for s in new_stocks])
            send_telegram_message(message)
            last_sent.update(new_stocks)

        stocks_display.markdown(
            f"### ✅ Stocks Fetched at {current_time}:\n\n" + "\n".join([f"- {s}" for s in stocks])
        )
        last_fetched = stocks
    else:
        stocks_display.markdown(f"⚠️ No stocks found at {current_time}.")

# Schedule to run every 5 minutes
schedule.every(5).minutes.do(run_screener)

# Run immediately at start
run_screener()

# Streamlit loop
while True:
    schedule.run_pending()
    time.sleep(1)
