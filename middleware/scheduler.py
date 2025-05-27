# middleware/scheduler.py

import asyncio
import time
from .retailer_scraper import get_argos_products, get_currys_products
from .ebay_api import get_ebay_resale_data
from .filter_logic import calculate_profit
from tgcf.plugins.sender import send_message

async def scan_and_notify():
    print("[INFO] Starting product scan and notification...")
    all_products = get_argos_products() + get_currys_products()
    for product in all_products:
        resale = get_ebay_resale_data(product["name"])
        profit = calculate_profit(product["price"], resale)
        if profit:
            msg = (
                f"🔥 *{product['name']}*\n"
                f"[Buy Now]({product['url']})\n"
                f"Retail: £{product['price']}\n"
                f"Avg. Resell: £{round(sum(resale)/len(resale), 2)}\n"
                f"Estimated Profit: *£{profit}*"
            )
            await send_message(msg, markdown=True)

async def scheduler_loop():
    while True:
        await scan_and_notify()
        print("[INFO] Waiting 50 minutes for next run...")
        await asyncio.sleep(50 * 60)  # 50 minutes

if __name__ == "__main__":
    asyncio.run(scheduler_loop())

