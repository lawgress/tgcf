import asyncio
from ebay_scraper.scheduler import scan_and_notify

if __name__ == "__main__":
    asyncio.run(scan_and_notify())