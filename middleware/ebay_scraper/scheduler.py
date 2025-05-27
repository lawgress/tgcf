from middleware.ebay_scraper.retailer_scraper import get_argos_products, get_currys_products
from middleware.ebay_scraper.ebay_api import get_ebay_resale_data
from middleware.ebay_scraper.filter_logic import calculate_profit
from middleware.ebay_scraper.send_to_tg import send_alert


async def scan_and_notify():
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
            send_alert(msg)

# Optional: Run manually if called directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(scan_and_notify())
