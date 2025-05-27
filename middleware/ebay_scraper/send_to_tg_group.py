import os
import requests

def send_alerts_to_group(alerts):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not bot_token or not chat_id:
        print("[WARN] BOT_TOKEN or CHAT_ID not set.")
        return

    for item in alerts:
        msg = (
            f"🔥 *{item['name']}*\n"
            f"[Buy Now]({item['url']})\n"
            f"Retail: £{item['price']}\n"
            f"Avg. Resell: £{item['resale_price']}\n"
            f"Estimated Profit: *£{item['profit']}*"
        )
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
        )
