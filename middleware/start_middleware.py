import asyncio
import os
from dotenv import load_dotenv

from middleware.retailer_scraper import get_argos_products, get_currys_products
from middleware.ebay_api import get_ebay_resale_data
from middleware.filter_logic import calculate_profit
from tgcf.plugins.sender import send_message

load_dotenv()

async def main():
    print("[INFO] Scraping products...")
    products = get_argos_products() + get_currys_products()

    print("[INFO] Checking resale values and filtering...")
    for product in products:
        resale_prices = get_ebay_resale_data(product["name"])
        if not resale_prices:
            continue
        
        profit = calculate_profit(product["price"], resale_prices)
        if profit:
            msg = (
                f"🔥 *{product['name']}*\n"
                f"[Buy Now]({product['url']})\n"
                f"Retail: £{product['price']}\n"
                f"Avg. Resell: £{round(sum(resale_prices)/len(resale_prices), 2)}\n"
                f"Estimated Profit: *£{profit}*"
            )
            print(f"[ALERT] Sending alert for: {product['name']}")
            await send_message(msg, markdown=True)

    print("[DONE] Alerts sent.")

if __name__ == "__main__":
    asyncio.run(main())
