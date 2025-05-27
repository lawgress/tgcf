import asyncio
import os
import logging
from fastapi import FastAPI
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import json

from middleware.retailer_scraper import get_argos_products, get_currys_products
from middleware.ebay_api import get_ebay_resale_data
from middleware.filter_logic import calculate_profit
from middleware.send_to_tg import send_message  # staging
# from middleware.send_to_tg_group import send_message  # prod version

load_dotenv()
app = FastAPI()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

async def alert_loop():
    while True:
        try:
            logging.info("[LOOP] Starting scrape & filter job...")
            products = get_argos_products() + get_currys_products()

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
                    logging.info(f"[ALERT] Sending: {product['name']}")
                    await send_message(msg, markdown=True)

            logging.info("[LOOP] Done. Sleeping...")
        except Exception as e:
            logging.error(f"[ERROR] Loop failed: {e}")

        await asyncio.sleep(180)  # wait 30 mins before next run

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(alert_loop())
