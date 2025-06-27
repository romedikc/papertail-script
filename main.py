import os
import requests
import time
import schedule
from datetime import datetime

TARGET_DATE = os.getenv("TARGET_DATE", "27.08.2025")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ASP_NET_SESSION_ID = os.getenv("ASP_NET_SESSION_ID")
CALENDAR_ID = os.getenv("CALENDAR_ID")
PERSON_COUNT = os.getenv("PERSON_COUNT", "1")


session = requests.Session()
session.cookies.update({
    'ASP.NET_SessionId': ASP_NET_SESSION_ID,
})
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/x-www-form-urlencoded',
})

form_data1 = {
    "Language": "ru",
    "Office": "ASTANA",
    "Command": "дальше"
}

form_data2 = {
    "Language": "ru",
    "Office": "ASTANA",
    "CalendarId": CALENDAR_ID,
    "Command": "дальше",
}

form_data3 = {
    "Language": "ru",
    "Office": "ASTANA",
    "CalendarId": CALENDAR_ID,
    "PersonCount": PERSON_COUNT,
    "Command": "дальше",
}

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def check_availability():
    try:
        session.post("https://appointment.bmeia.gv.at/", data=form_data1)
        session.post("https://appointment.bmeia.gv.at/", data=form_data2)
        response = session.post("https://appointment.bmeia.gv.at/", data=form_data3)
    except Exception as e:
        print(f"Request error: {e}")
        return False

    if TARGET_DATE in response.text:
        msg = f"{TARGET_DATE} is now available! Go book it! https://appointment.bmeia.gv.at"
        send_telegram_alert(msg)
        return True
    else:
        print(f"{TARGET_DATE} not available yet.")
        return False

check_availability()

schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_availability)

while True:
    schedule.run_pending()
    time.sleep(1)
