from telegram import Bot
import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("STAGING_CHAT_ID")  # Or hardcode for test: CHAT_ID = '123456789'

bot = Bot(token=TG_BOT_TOKEN)

def send_alert(message: str):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print("[INFO] Message sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
