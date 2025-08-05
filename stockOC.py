from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from datetime import datetime

BOT_TOKEN = "7735892458:AAELFRclang2MgJwO2Rd9RRwNmoll1LzlFg"
CHAT_ID = "5073531512"
SCREENER_URL = "https://intradayscreener.com/scan/26118/Raja_%285min_%2B_15min%29"

previous_stocks = []

# Chrome options setup
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless for background operation
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up the service for ChromeDriver
service = Service(ChromeDriverManager().install())

# Initialize the WebDriver with specified options
driver = webdriver.Chrome(service=service, options=chrome_options)

def fetch_screener_stocks():
    try:
        driver.get(SCREENER_URL)
        # Wait for the table to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "mat-table"))
        )

        # Find the table element after it loads
        table = driver.find_element(By.TAG_NAME, "mat-table")
        rows = table.find_elements(By.TAG_NAME, "mat-row")

        stocks = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "mat-cell")
            if cells:
                stocks.append(cells[0].text.strip())

        print(f"🟡 Fetched stocks: {stocks}")
        return stocks

    except Exception as e:
        print(f"❌ Error fetching stocks: {e}")
        return []

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=data)

def check_for_new_stocks():
    global previous_stocks
    current_stocks = fetch_screener_stocks()

    if not current_stocks:
        print("⚠️ No stocks found.")
        return

    new_stocks = [s for s in current_stocks if s not in previous_stocks]
    if new_stocks:
        message = f"📈 *New BULLISH Stocks at {datetime.now().strftime('%H:%M:%S')}*\n\n" + "\n".join(f"🔸 {s}" for s in new_stocks)
        send_telegram_message(message)
        previous_stocks = current_stocks
    else:
        print("✅ No new stocks.")

# Run every 5 minutes
while True:
    print(f"\n⏰ Checking screener at {datetime.now().strftime('%H:%M:%S')}...")
    check_for_new_stocks()
    time.sleep(300)  # Wait 5 minutes
