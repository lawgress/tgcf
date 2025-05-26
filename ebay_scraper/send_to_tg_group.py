import os
import json
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("STAGING_CHAT_ID")  # Example: -1001234567890

def send_alerts_to_group():
    try:
        with open("ebay_scraper/output/alerts.json", "r") as f:
            alerts = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load alerts: {e}")
        return

    for alert in alerts:
        try:
            title = alert.get("title", "No Title")
            retail = alert.get("retail_price", "N/A")
            ebay = alert.get("ebay_avg_price", "N/A")
            profit = alert.get("profit", "N/A")
            sold = alert.get("recent_sold_count", "N/A")
            url = alert.get("product_url", "")

            msg = f"""
🔥 {title}
Retail: £{retail} | eBay: £{ebay}
Profit: £{profit} | Sold: {sold}x
{url}
""".strip()

            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": msg,
                    "disable_web_page_preview": True
                }
            )
        except Exception as e:
            print(f"[ERROR] Sending failed: {e}")
