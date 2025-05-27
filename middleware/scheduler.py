import asyncio
import os
from fastapi import FastAPI
from datetime import datetime

import asyncio
import os
from middleware.ebay_scraper.retailer_scraper import get_argos_products, get_currys_products
from middleware.ebay_scraper.ebay_api import get_ebay_resale_data
from middleware.ebay_scraper.filter_logic import calculate_profit
from middleware.ebay_scraper.send_to_tg_group import send_alerts_to_group
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Global variable to store last log
last_log = {
    "last_run": None,
    "products_found": 0,
    "alerts_sent": 0
}

@app.get("/")
def read_root():
    return {
        "status": "Bot running",
        "last_log": last_log
    }

async def run_scheduler_loop():
    while True:
        print("[INFO] Scraping started...")
        try:
            products = get_argos_products() + get_currys_products()
            resale_data = get_ebay_resale_data(products)
            filtered = calculate_profit(resale_data)
            send_alerts_to_group(filtered)

            # Update last log
            last_log["last_run"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            last_log["products_found"] = len(products)
            last_log["alerts_sent"] = len(filtered)

            print(f"[INFO] Cycle completed: {len(filtered)} alerts sent.")
        except Exception as e:
            print("[ERROR]", e)

        print("[INFO] Sleeping for 60 minutes...\n")
        await asyncio.sleep(60 * 60)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_scheduler_loop())
    import uvicorn
    uvicorn.run("middleware.scheduler:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
