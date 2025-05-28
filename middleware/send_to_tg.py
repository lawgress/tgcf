import os
from telegram import Bot
from telegram.error import TelegramError

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("STAGING_CHAT_ID")  # Or replace with your actual group/user ID

# Validate environment setup
if not TG_BOT_TOKEN or not CHAT_ID:
    raise EnvironmentError("Missing TG_BOT_TOKEN or STAGING_CHAT_ID environment variables.")

bot = Bot(token=TG_BOT_TOKEN)

def send_message(message: str):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print("[INFO] Telegram message sent successfully.")
    except TelegramError as e:
        print(f"[ERROR] Telegram API error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while sending Telegram message: {e}")
