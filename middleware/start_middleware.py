import asyncio
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from retailer_scraper import get_argos_products, get_currys_products
from ebay_api import get_ebay_resale_data
from filter_logic import calculate_profit
from send_to_tg import send_message  # staging
# from middleware.send_to_tg_group import send_message  # prod version

# Load .env variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
)
logger = logging.getLogger(__name__)

# FastAPI App with lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting middleware FastAPI app...")
    asyncio.create_task(alert_loop())
    yield
    logger.info("🛑 Shutting down middleware app...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "🟢 Middleware is running"}

@app.get("/debug")
def debug():
    logger.info("[DEBUG] Ping received")
    return {"message": "pong"}

# Alert loop runs on startup
async def alert_loop():
    while True:
        try:
            logger.info("[LOOP] Starting scrape & filter job...")
            argos = get_argos_products()
            currys = get_currys_products()
            products = argos + currys
            logger.info(f"[LOOP] Total products scraped: {len(products)}")

            if not products:
                logger.warning("[LOOP] No products found. Skipping iteration.")
                await asyncio.sleep(180)
                continue

            for product in products:
                logger.info(f"[PRODUCT] Checking: {product['name']} (£{product['price']})")

                resale_prices = get_ebay_resale_data(product["name"])
                if not resale_prices:
                    logger.info(f"[EBAY] No resale data found for: {product['name']}")
                    continue

                profit = calculate_profit(product["price"], resale_prices)
                if profit:
                    avg_resell = round(sum(resale_prices) / len(resale_prices), 2)
                    msg = (
                        f"🔥 *{product['name']}*\n"
                        f"[Buy Now]({product['url']})\n"
                        f"Retail: £{product['price']}\n"
                        f"Avg. Resell: £{avg_resell}\n"
                        f"Estimated Profit: *£{profit}*"
                    )
                    logger.info(f"[ALERT] Profitable item found: {product['name']} (£{profit})")
                    await send_message(msg, markdown=True)
                else:
                    logger.info(f"[SKIP] No profit on: {product['name']}")

            logger.info("[LOOP] Job completed. Sleeping for 3 minutes...")

        except Exception as e:
            logger.exception(f"[ERROR] Alert loop failed: {e}")

        await asyncio.sleep(180)  # Sleep for 3 minutes

# If running locally or for debugging (optional)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("start_middleware:app", host="0.0.0.0", port=port, reload=True)
