import sys
import os
import json
import argparse
import logging
from dotenv import load_dotenv

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Ensure root directory is in Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ebay_scraper.scraper import scrape_products
from ebay_scraper.ebay_api import check_resale_value
from ebay_scraper.filter_logic import filter_profitable_items
from ebay_scraper.send_to_tg_group import send_alerts_to_group

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def run_pipeline(dry_run=False):
    try:
        logger.info("Scraping products...")
        raw_products = scrape_products()

        logger.info("Checking resale values...")
        enriched = check_resale_value(raw_products)

        logger.info("Filtering profitable items...")
        filtered = filter_profitable_items(enriched)

        # Save output for backup
        output_dir = os.path.join("ebay_scraper", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "alerts.json")
        with open(output_path, "w") as f:
            json.dump(filtered, f, indent=2)
        logger.info(f"Saved filtered results to {output_path}")

        if dry_run:
            logger.info("Dry run mode: Skipping Telegram alerts.")
        else:
            logger.info("Sending to Telegram group...")
            send_alerts_to_group(filtered)

    except Exception as e:
        logger.exception("Pipeline failed: %s", str(e))


def main():
    parser = argparse.ArgumentParser(description="eBay Flip Alert Bot")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending Telegram alerts")
    parser.add_argument("--schedule", type=int, help="Interval (in minutes) to rerun the pipeline")

    args = parser.parse_args()

    if args.schedule:
        logger.info(f"Scheduled mode: Running every {args.schedule} minutes.")
        scheduler = BlockingScheduler()

        scheduler.add_job(
            lambda: run_pipeline(dry_run=args.dry_run),
            'interval',
            minutes=args.schedule,
            next_run_time=datetime.now()
        )

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
    else:
        run_pipeline(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
