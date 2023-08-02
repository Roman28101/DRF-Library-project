import os

import requests
from dotenv import load_dotenv


load_dotenv()


def send_to_telegram(message=None):

    apiToken = os.environ.get("TELEGRAM_TOKEN")
    chatID = os.environ.get("CHAT_ID")
    apiURL = f"https://api.telegram.org/bot{apiToken}/sendMessage"

    try:
        requests.post(apiURL, json={"chat_id": chatID, "text": message})
    except Exception as e:
        return e
