
import requests
from bs4 import BeautifulSoup
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def fetch_html(url):
    try:
        logging.info(f"Fetching URL: {url}")
        time.sleep(random.uniform(1, 3)) # Anti-bot measure
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logging.warning(f"Failed to fetch {url}: {e}")
        return None


def extract_products(soup, base_url, retailer_name):
    if not soup:
        return []

    products = []
    selectors = [
        "a[data-test='component-product-card-title']",
        ".product-card-title a",
        ".ProductCardstyles__Title-sc-__sc-1gqy9lc-0 a",
        "h3 a"
    ]

    for selector in selectors:
        items = soup.select(selector)
        if items:
            logging.info(f"{retailer_name}: Found {len(items)} products with selector {selector}")
            for item in items:
                try:
                    name = item.get_text(strip=True)
                    href = item.get("href", "")
                    if not href.startswith("http"):
                        url = base_url.rstrip("/") + href
                    else:
                        url = href

                    container = item.find_parent("article") or item.find_parent("div")

                    # Try multiple price selectors
                    price = "Unknown"
                    for price_sel in ["[data-test='price-current']", ".price", ".price-current"]:
                        price_elem = container.select_one(price_sel) if container else None
                        if price_elem:
                            price = price_elem.get_text(strip=True)
                            break

                    image = None
                    if container:
                        img = container.find("img")
                        if img:
                            image = img.get("src") or img.get("data-src")

                    products.append({
                        "name": name,
                        "url": url,
                        "price": price,
                        "image": image,
                        "retailer": retailer_name
                    })
                except Exception as e:
                    logging.warning(f"Error parsing product: {e}")
            break # Use first working selector

    return products


def get_argos_products():
    urls = [
        "https://www.argos.co.uk/category/33000986/smart-tech/",
        "https://www.argos.co.uk/category/33006/technology/",
        "https://www.argos.co.uk/category/33007/laptops-and-pcs/",
        "https://www.argos.co.uk/category/33008/mobile-phones-and-accessories/",
        "https://www.argos.co.uk/category/33013/tablets-and-ereaders/"
    ]
    all_products = []
    for url in urls:
        soup = fetch_html(url)
        all_products.extend(extract_products(soup, "https://www.argos.co.uk", "Argos"))

    return deduplicate(all_products)


def get_currys_products():
    urls = [
        "https://www.currys.co.uk/smart-tech",
        "https://www.currys.co.uk/computing",
        "https://www.currys.co.uk/computing/laptops",
        "https://www.currys.co.uk/phones-broadband-and-sat-nav/mobile-phones",
        "https://www.currys.co.uk/computing/tablets-and-ereaders",
        "https://www.currys.co.uk/gaming",
        "https://www.currys.co.uk/cameras-and-camcorders"
    ]
    all_products = []
    for url in urls:
        soup = fetch_html(url)
        all_products.extend(extract_products(soup, "https://www.currys.co.uk", "Currys"))

    return deduplicate(all_products)


def deduplicate(products):
    seen = set()
    unique = []
    for p in products:
        key = (p['name'], p['url'])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    logging.info(f"Total unique products: {len(unique)}")
    return unique


if __name__ == "__main__":
    logging.info("Starting product scraping...")

    argos = get_argos_products()
    logging.info(f"Argos products scraped: {len(argos)}")
    for p in argos[:3]:
        logging.info(f"{p['name']} | {p['price']} | {p['url']}")

    currys = get_currys_products()
    logging.info(f"Currys products scraped: {len(currys)}")
    for p in currys[:3]:
        logging.info(f"{p['name']} | {p['price']} | {p['url']}")

    logging.info("Scraping finished. Ready for middleware filtering and eBay check.")
