import tkinter as tk
from tkinter import messagebox
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Telegram bot settings
BOT_TOKEN = "7735892458:AAELFRclang2MgJwO2Rd9RRwNmoll1LzlFg"
CHAT_ID = "5073531512"
SCREENER_URL = "https://intradayscreener.com/scan/26118/Raja_%285min_%2B_15min%29"

previous_stocks = []

# Tkinter GUI setup
root = tk.Tk()
root.title("Stock Screener Alert Bot")

# Set up the GUI components
status_label = tk.Label(root, text="Status: Waiting to start...", width=50)
status_label.pack(pady=10)

log_label = tk.Label(root, text="Log:", width=50, anchor="w")
log_label.pack(pady=10)

log_text = tk.Text(root, height=10, width=50)
log_text.pack(pady=10)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=data)

def fetch_screener_stocks():
    try:
        options = Options()
        options.add_argument("--headless")  # Run headless for background operation
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        driver.get(SCREENER_URL)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "mat-table"))
        )

        table = driver.find_element(By.TAG_NAME, "mat-table")
        rows = table.find_elements(By.TAG_NAME, "mat-row")
        stocks = []

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "mat-cell")
            if cells:
                stocks.append(cells[0].text.strip())

        driver.quit()
        return stocks

    except Exception as e:
        print(f"❌ Error fetching stocks: {e}")
        return []

def check_for_new_stocks():
    global previous_stocks
    current_stocks = fetch_screener_stocks()

    if not current_stocks:
        log_text.insert(tk.END, "⚠️ No stocks found.\n")
        return

    new_stocks = [s for s in current_stocks if s not in previous_stocks]
    if new_stocks:
        message = f"📈 *New Stocks at {datetime.now().strftime('%H:%M:%S')}*\n\n" + "\n".join(f"🔸 {s}" for s in new_stocks)
        send_telegram_message(message)
        log_text.insert(tk.END, f"New stocks found: {new_stocks}\n")
        previous_stocks = current_stocks
    else:
        log_text.insert(tk.END, "✅ No new stocks.\n")

    log_text.yview(tk.END)  # Scroll to the bottom

def start_checking():
    status_label.config(text="Status: Checking every 5 minutes...")
    root.after(300000, start_checking)  # Call this function every 5 minutes
    check_for_new_stocks()

def stop_checking():
    status_label.config(text="Status: Stopped.")
    log_text.insert(tk.END, "✅ Stopped the checking.\n")

# Start/Stop buttons
start_button = tk.Button(root, text="Start Checking", command=start_checking, width=20)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Checking", command=stop_checking, width=20)
stop_button.pack(pady=5)

# Run the GUI
root.mainloop()
