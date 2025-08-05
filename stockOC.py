import streamlit as st
import time
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Telegram Bot Details
BOT_TOKEN = "7735892458:AAELFRclang2MgJwO2Rd9RRwNmoll1LzlFg"
CHAT_ID = "5073531512"
SCREENER_URL = "https://intradayscreener.com/scan/26118/Raja_%285min_%2B_15min%29"

previous_stocks = []

st.set_page_config(page_title="Live Stock Screener", layout="wide")
st.title("📈 Real-time Stock Screener Dashboard")

log_box = st.empty()
stocks_display = st.empty()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': message})

def fetch_stocks():
    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(SCREENER_URL)
        time.sleep(5)
        table = driver.find_element(By.TAG_NAME, "mat-table")
        rows = table.find_elements(By.TAG_NAME, "mat-row")
        stocks = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "mat-cell")
            if cells:
                stocks.append(cells[0].text.strip())

        return stocks

    except Exception as e:
        st.error(f"❌ Error fetching stocks: {e}")
        return []

    finally:
        driver.quit()

def run_screener():
    global previous_stocks

    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        stocks = fetch_stocks()

        if not stocks:
            log_box.warning(f"[{current_time}] ⚠️ No stocks found.")
        else:
            new_stocks = [s for s in stocks if s not in previous_stocks]

            if new_stocks:
                msg = f"📈 *New Stocks at {current_time}*\n\n" + "\n".join(f"🔸 {s}" for s in new_stocks)
                send_telegram_message(msg)
                log_box.success(f"[{current_time}] ✅ New stocks: {', '.join(new_stocks)}")
                stocks_display.write(f"🆕 Stocks at {current_time}:\n\n" + "\n".join(new_stocks))
                previous_stocks = stocks
            else:
                log_box.info(f"[{current_time}] No new stocks.")
        
        time.sleep(300)  # every 5 minutes

if st.button("🚀 Start Screener"):
    run_screener()
