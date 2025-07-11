import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SITES = os.getenv("SITES", "").split(",")

print(f"Token: {TELEGRAM_TOKEN}")
print(f"Chat ID: {TELEGRAM_CHAT_ID}")
print(f"Sites: {SITES}")