import os
import re

import requests
import time
import schedule
from datetime import datetime

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CALENDAR_ID = os.getenv("CALENDAR_ID")
PERSON_COUNT = os.getenv("PERSON_COUNT", "1")


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

def find_target_dates(text):
    pattern = r'(\b\d{2})\.(\d{2})\.(\d{4})\b'
    matches = re.findall(pattern, text)
    valid_dates = []

    for day_str, month_str, year_str in matches:
        day = int(day_str)
        month = int(month_str)

        if month == 7:
            valid_dates.append(f"{day_str}.{month_str}.{year_str}")
        elif month == 8 and day <= 20:
            valid_dates.append(f"{day_str}.{month_str}.{year_str}")

    return valid_dates

def check_availability():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded',
    })

    try:
        session.get("https://appointment.bmeia.gv.at/")
    except Exception as e:
        print(f"Initial GET request failed: {e}")
        return False

    try:
        session.post("https://appointment.bmeia.gv.at/", data={
            "Language": "ru",
            "Office": "ASTANA",
            "Command": "дальше"
        })

        session.post("https://appointment.bmeia.gv.at/", data={
            "Language": "ru",
            "Office": "ASTANA",
            "CalendarId": CALENDAR_ID,
            "Command": "дальше"
        })

        response = session.post("https://appointment.bmeia.gv.at/", data={
            "Language": "ru",
            "Office": "ASTANA",
            "CalendarId": CALENDAR_ID,
            "PersonCount": PERSON_COUNT,
            "Command": "дальше"
        })
    except Exception as e:
        print(f"Form submission failed: {e}")
        return False

    found = find_target_dates(response.text)

    if found:
        msg = f"✅ Appointment found for July or August! Go book it: https://appointment.bmeia.gv.at"
        send_telegram_alert(msg)
        return True
    else:
        print("❌ No available dates in July or August yet.")
        return False

if __name__ == "__main__":
    check_availability()

    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_availability)

    while True:
        schedule.run_pending()
        time.sleep(1)
