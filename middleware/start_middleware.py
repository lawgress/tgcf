from retailers.argos import get_argos_products
from filter_logic import is_profitable

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting middleware FastAPI app...")
    while True:
        print("[LOOP] Starting scrape & filter job...")

        # ✅ Force test product
        products = get_argos_products()

        if not products:
            print("[LOOP] No products found. Skipping iteration.")
        else:
            print(f"[LOOP] Total products scraped: {len(products)}")

            for product in products:
                print(f"[DEBUG] Raw: {product}")
                # Optional: test filtering logic
                if is_profitable(product):
                    print(f"[✅] PROFITABLE: {product['name']}")
                else:
                    print(f"[❌] Not profitable: {product['name']}")

        await asyncio.sleep(60 * 5)  # 5-minute wait
