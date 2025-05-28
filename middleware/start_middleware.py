from retailer_scraper import get_argos_products
from filter_logic import is_profitable

from fastapi import FastAPI
import asyncio
from send_to_tg import send_message  # staging

app = FastAPI()  # ✅ Define the FastAPI app BEFORE decorators



from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting middleware FastAPI app...")

    async def background_loop():
        while True:
            print("[LOOP] Starting scrape & filter job...")
            products = get_argos_products()
            print(f"[LOOP] Total products scraped: {len(products)}")
            if not products:
                print("[LOOP] No products found. Skipping iteration.")
            for product in products:
                print(f"[DEBUG] Product: {product['name']}")
                send_to_tg_group(product)
            await asyncio.sleep(180)

    # Start loop
    asyncio.create_task(background_loop())
    yield  # Lifespan active
    print("🛑 Middleware shutting down...")

app = FastAPI(lifespan=lifespan)
