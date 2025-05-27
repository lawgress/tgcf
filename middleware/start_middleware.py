import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ebay_scraper.retailer_scraper import scrape_products
from ebay_scraper.ebay_api import check_resale_value
from ebay_scraper.filter_logic import filter_profitable_items
from ebay_scraper.send_to_tg_group import send_alerts_to_group

from dotenv import load_dotenv
import json

load_dotenv()

def main():
    print("[INFO] Scraping products...")
    raw_products = scrape_products()

    print("[INFO] Checking resale values...")
    enriched = check_resale_value(raw_products)

    print("[INFO] Filtering profitable items...")
    filtered = filter_profitable_items(enriched)

    with open("ebay_scraper/output/alerts.json", "w") as f:
        json.dump(filtered, f, indent=2)

    print("[INFO] Sending to Telegram group...")
    send_alerts_to_group(filtered)

if __name__ == "__main__":
    main()
