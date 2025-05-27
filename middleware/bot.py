import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailerScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page(self, url, retries=3):
        """Fetch a page with retry logic and error handling"""
        for attempt in range(retries):
            try:
                # Add random delay to avoid being blocked
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
        return None

    def extract_price(self, price_text):
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove common currency symbols and text
        import re
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        return float(price_match.group()) if price_match else None

    def get_argos_products(self, search_term=None, category_url=None):
        """Enhanced Argos product scraper"""
        products = []
        
        if search_term:
            url = f"https://www.argos.co.uk/search/{search_term}/"
        elif category_url:
            url = category_url
        else:
            url = "https://www.argos.co.uk/category/33000986/smart-tech/"
        
        logger.info(f"Scraping Argos: {url}")
        soup = self.get_page(url)
        
        if not soup:
            return products
        
        # Multiple selectors to catch different layouts
        product_selectors = [
            ".ProductCardstyles__Title-sc-__sc-1gqy9lc-0",
            "[data-test='product-title']",
            ".product-card-title",
            "h3[data-test='component-product-card-title']"
        ]
        
        for selector in product_selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"Found {len(items)} products with selector: {selector}")
                break
        
        for item in items:
            try:
                # Extract product name
                name = item.get_text(strip=True) if item else "Unknown Product"
                
                # Find parent container for additional data
                product_container = item.find_parent(['article', 'div'], class_=lambda x: x and 'product' in x.lower() if x else False)
                if not product_container:
                    product_container = item.find_parent(['div'] * 5)  # Go up 5 levels
                
                # Extract link
                link_elem = item.find('a') or (product_container.find('a') if product_container else None)
                link = urljoin("https://www.argos.co.uk", link_elem.get('href')) if link_elem else None
                
                # Extract price with multiple selectors
                price_selectors = [
                    "[data-test='price-current']",
                    ".price",
                    "[data-test='price']",
                    ".product-price"
                ]
                
                price_text = None
                if product_container:
                    for price_sel in price_selectors:
                        price_elem = product_container.select_one(price_sel)
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            break
                
                # Extract image
                img_elem = None
                if product_container:
                    img_elem = product_container.find('img')
                image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
                
                # Extract rating if available
                rating_elem = None
                if product_container:
                    rating_elem = product_container.select_one("[data-test='rating']") or \
                                product_container.select_one(".rating")
                rating = rating_elem.get_text(strip=True) if rating_elem else None
                
                product_data = {
                    "name": name,
                    "url": link,
                    "price": price_text,
                    "price_numeric": self.extract_price(price_text),
                    "image": image_url,
                    "rating": rating,
                    "retailer": "Argos"
                }
                
                products.append(product_data)
                
            except Exception as e:
                logger.warning(f"Error processing Argos product: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(products)} products from Argos")
        return products

    def get_currys_products(self, search_term=None, category_url=None):
        """Enhanced Currys product scraper"""
        products = []
        
        if search_term:
            url = f"https://www.currys.co.uk/search?q={search_term}"
        elif category_url:
            url = category_url
        else:
            url = "https://www.currys.co.uk/smart-tech"
        
        logger.info(f"Scraping Currys: {url}")
        soup = self.get_page(url)
        
        if not soup:
            return products
        
        # Multiple selectors for Currys
        product_selectors = [
            "a.ProductCardstyles__Title",
            "[data-test='product-title']",
            ".product-title",
            "h3 a"
        ]
        
        for selector in product_selectors:
            items = soup.select(selector)
            if items:
                logger.info(f"Found {len(items)} products with selector: {selector}")
                break
        
        for item in items:
            try:
                # Extract product name
                name = item.get_text(strip=True) if item else "Unknown Product"
                
                # Extract link
                link = urljoin("https://www.currys.co.uk", item.get('href')) if item.get('href') else None
                
                # Find product container
                product_container = item.find_parent(['article', 'div'], class_=lambda x: x and 'product' in x.lower() if x else False)
                if not product_container:
                    product_container = item.find_parent(['div'] * 5)
                
                # Extract price with multiple selectors
                price_selectors = [
                    "[data-test='price-current']",
                    ".price-current",
                    ".price",
                    "[data-test='price']"
                ]
                
                price_text = None
                if product_container:
                    for price_sel in price_selectors:
                        price_elem = product_container.select_one(price_sel)
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            break
                
                # Extract image
                img_elem = None
                if product_container:
                    img_elem = product_container.find('img')
                image_url = img_elem.get('src') or img_elem.get('data-src') if img_elem else None
                
                # Extract brand if available
                brand_elem = None
                if product_container:
                    brand_elem = product_container.select_one("[data-test='brand']") or \
                               product_container.select_one(".brand")
                brand = brand_elem.get_text(strip=True) if brand_elem else None
                
                product_data = {
                    "name": name,
                    "url": link,
                    "price": price_text,
                    "price_numeric": self.extract_price(price_text),
                    "image": image_url,
                    "brand": brand,
                    "retailer": "Currys"
                }
                
                products.append(product_data)
                
            except Exception as e:
                logger.warning(f"Error processing Currys product: {e}")
                continue
        
        logger.info(f"Successfully scraped {len(products)} products from Currys")
        return products

    def get_all_products(self, search_term=None):
        """Get products from all retailers"""
        all_products = []
        
        # Get products from Argos
        argos_products = self.get_argos_products(search_term=search_term)
        all_products.extend(argos_products)
        
        # Get products from Currys
        currys_products = self.get_currys_products(search_term=search_term)
        all_products.extend(currys_products)
        
        return all_products

    def save_to_file(self, products, filename="scraped_products.json"):
        """Save products to JSON file"""
        import json
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(products)} products to {filename}")

    def compare_prices(self, products):
        """Compare prices across retailers for similar products"""
        price_comparison = {}
        
        for product in products:
            if product.get('price_numeric'):
                name_key = product['name'].lower()[:30]  # Use first 30 chars as key
                
                if name_key not in price_comparison:
                    price_comparison[name_key] = []
                
                price_comparison[name_key].append({
                    'retailer': product['retailer'],
                    'name': product['name'],
                    'price': product['price_numeric'],
                    'url': product['url']
                })
        
        # Find best deals
        best_deals = {}
        for product_name, retailers in price_comparison.items():
            if len(retailers) > 1:  # Only compare if available from multiple retailers
                sorted_retailers = sorted(retailers, key=lambda x: x['price'])
                best_deals[product_name] = {
                    'cheapest': sorted_retailers[0],
                    'all_prices': sorted_retailers
                }
        
        return best_deals


# Usage example
if __name__ == "__main__":
    scraper = RetailerScraper()
    
    # Scrape products with search term
    products = scraper.get_all_products(search_term="laptop")
    
    # Print first few products
    for i, product in enumerate(products[:50]):
        print(f"{i+1}. {product['name']}")
        print(f"   Retailer: {product['retailer']}")
        print(f"   Price: {product['price']}")
        print(f"   URL: {product['url']}")
        print("-" * 50)
    
    # Save to file
    scraper.save_to_file(products)
    
    # Compare prices
    price_comparison = scraper.compare_prices(products)
    
    print(f"\nFound {len(products)} products total")
    print(f"Price comparisons available for {len(price_comparison)} products")
