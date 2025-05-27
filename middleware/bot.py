import requests
from bs4 import BeautifulSoup
import time
import random
import json
import re
from datetime import datetime

def get_argos_products():
    """Enhanced Argos product scraper to grab more products including presales"""
    products = []
    
    # Multiple category URLs to scrape more products
    urls = [
        "https://www.argos.co.uk/category/33000986/smart-tech/",
        "https://www.argos.co.uk/category/33006/technology/",
        "https://www.argos.co.uk/category/33007/laptops-and-pcs/",
        "https://www.argos.co.uk/category/33008/mobile-phones-and-accessories/",
        "https://www.argos.co.uk/category/33013/tablets-and-ereaders/",
        "https://www.argos.co.uk/category/33016/tv-and-entertainment/",
        "https://www.argos.co.uk/category/33018/cameras-and-camcorders/",
        "https://www.argos.co.uk/category/33020/gaming/",
        "https://www.argos.co.uk/category/33004/home-and-garden/",
        "https://www.argos.co.uk/category/33005/sports-and-leisure/",
        "https://www.argos.co.uk/category/33002/health-and-beauty/",
        "https://www.argos.co.uk/category/33001/clothing/"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for url in urls:
        try:
            # Add delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Multiple selectors to catch different product layouts
            product_selectors = [
                ".ProductCardstyles__Title-sc-__sc-1gqy9lc-0",
                "[data-test='component-product-card-title']",
                ".product-card-title",
                "h3 a",
                ".ProductCardstyles__Title",
                "[data-test='product-title']"
            ]
            
            items = []
            for selector in product_selectors:
                items = soup.select(selector)
                if items:
                    break
            
            for item in items:
                try:
                    # Get product name
                    if item.name == 'a':
                        name = item.get_text(strip=True)
                        link_elem = item
                    else:
                        name = item.get_text(strip=True)
                        link_elem = item.find('a')
                    
                    if not name:
                        continue
                    
                    # Get product link
                    if link_elem and link_elem.get('href'):
                        if link_elem['href'].startswith('http'):
                            link = link_elem['href']
                        else:
                            link = "https://www.argos.co.uk" + link_elem['href']
                    else:
                        link = url
                    
                    # Find product container for price
                    product_container = item.find_parent(['article', 'div'], class_=lambda x: x and ('product' in x.lower() or 'card' in x.lower()) if x else False)
                    if not product_container:
                        # Try going up several levels to find container
                        current = item
                        for _ in range(5):
                            current = current.find_parent()
                            if current and current.get('class'):
                                class_str = ' '.join(current.get('class', []))
                                if 'product' in class_str.lower() or 'card' in class_str.lower():
                                    product_container = current
                                    break
                    
                    # Get price with multiple selectors
                    price = "Price not found"
                    is_presale = False
                    availability = "In Stock"
                    
                    if product_container:
                        price_selectors = [
                            "[data-test='price-current']",
                            ".price-current",
                            ".price",
                            "[data-test='price']",
                            ".ProductCardstyles__Price",
                            ".product-price"
                        ]
                        
                        for price_sel in price_selectors:
                            price_elem = product_container.select_one(price_sel)
                            if price_elem:
                                price = price_elem.get_text(strip=True)
                                break
                        
                        # Check for presale/preorder indicators
                        presale_indicators = [
                            "pre-order", "preorder", "pre order", "coming soon", 
                            "available from", "release date", "expected", "presale"
                        ]
                        
                        availability_elem = product_container.select_one("[data-test='availability']") or \
                                          product_container.select_one(".availability") or \
                                          product_container.select_one(".stock-status")
                        
                        if availability_elem:
                            availability_text = availability_elem.get_text(strip=True).lower()
                            availability = availability_elem.get_text(strip=True)
                            for indicator in presale_indicators:
                                if indicator in availability_text:
                                    is_presale = True
                                    break
                        
                        # Also check product name for presale indicators
                        name_lower = name.lower()
                        for indicator in presale_indicators:
                            if indicator in name_lower:
                                is_presale = True
                                break
                    
                    # Get additional product details
                    image_url = None
                    rating = None
                    if product_container:
                        # Get image
                        img_elem = product_container.find('img')
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                        
                        # Get rating
                        rating_elem = product_container.select_one("[data-test='rating']") or product_container.select_one(".rating")
                        if rating_elem:
                            rating = rating_elem.get_text(strip=True)
                    
                    product_data = {
                        "name": name,
                        "url": link,
                        "price": price,
                        "image": image_url,
                        "rating": rating,
                        "availability": availability,
                        "is_presale": is_presale,
                        "retailer": "Argos",
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    products.append(product_data)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue
    
    # Remove duplicates based on product name and URL
    seen = set()
    unique_list = []
    for product in products:
        identifier = (product['name'], product['url'])
        if identifier not in seen:
            seen.add(identifier)
            unique_list.append(product)
    
    products = unique_list
    return products

def get_currys_products():
    """Enhanced Currys product scraper to grab more products including presales"""
    products = []
    
    # Multiple category URLs to scrape more products
    urls = [
        "https://www.currys.co.uk/smart-tech",
        "https://www.currys.co.uk/computing",
        "https://www.currys.co.uk/computing/laptops",
        "https://www.currys.co.uk/phones-broadband-and-sat-nav/mobile-phones",
        "https://www.currys.co.uk/computing/tablets-and-ereaders",
        "https://www.currys.co.uk/gaming",
        "https://www.currys.co.uk/cameras-and-camcorders",
        "https://www.currys.co.uk/tv-and-entertainment",
        "https://www.currys.co.uk/home-appliances",
        "https://www.currys.co.uk/small-kitchen-appliances",
        "https://www.currys.co.uk/health-and-beauty",
        "https://www.currys.co.uk/sport-and-leisure"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for url in urls:
        try:
            # Add delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Multiple selectors for Currys products
            product_selectors = [
                "a.ProductCardstyles__Title",
                "[data-test='product-title'] a",
                ".product-title a",
                "h3 a",
                ".ProductCard a",
                "[data-test='component-product-card-title'] a"
            ]
            
            items = []
            for selector in product_selectors:
                items = soup.select(selector)
                if items:
                    break
            
            for item in items:
                try:
                    # Get product name and link
                    name = item.get_text(strip=True)
                    if not name:
                        continue
                    
                    # Get product link
                    if item.get('href'):
                        if item['href'].startswith('http'):
                            link = item['href']
                        else:
                            link = "https://www.currys.co.uk" + item['href']
                    else:
                        link = url
                    
                    # Find product container for additional data
                    product_container = item.find_parent(['article', 'div'], class_=lambda x: x and ('product' in x.lower() or 'card' in x.lower()) if x else False)
                    if not product_container:
                        # Try going up several levels
                        current = item
                        for _ in range(5):
                            current = current.find_parent()
                            if current and current.get('class'):
                                class_str = ' '.join(current.get('class', []))
                                if 'product' in class_str.lower() or 'card' in class_str.lower():
                                    product_container = current
                                    break
                    
                    # Get price with multiple selectors
                    price = "Price not found"
                    is_presale = False
                    availability = "In Stock"
                    
                    if product_container:
                        price_selectors = [
                            "[data-test='price-current']",
                            ".price-current",
                            ".price",
                            "[data-test='price']",
                            ".ProductCardstyles__Price",
                            ".product-price",
                            ".price-info"
                        ]
                        
                        for price_sel in price_selectors:
                            price_elem = product_container.select_one(price_sel)
                            if price_elem:
                                price = price_elem.get_text(strip=True)
                                break
                        
                        # Check for presale/preorder indicators
                        presale_indicators = [
                            "pre-order", "preorder", "pre order", "coming soon", 
                            "available from", "release date", "expected", "presale"
                        ]
                        
                        availability_elem = product_container.select_one("[data-test='availability']") or \
                                          product_container.select_one(".availability") or \
                                          product_container.select_one(".stock-status")
                        
                        if availability_elem:
                            availability_text = availability_elem.get_text(strip=True).lower()
                            availability = availability_elem.get_text(strip=True)
                            for indicator in presale_indicators:
                                if indicator in availability_text:
                                    is_presale = True
                                    break
                        
                        # Also check product name for presale indicators
                        name_lower = name.lower()
                        for indicator in presale_indicators:
                            if indicator in name_lower:
                                is_presale = True
                                break
                    
                    # Get additional product details
                    image_url = None
                    brand = None
                    if product_container:
                        # Get image
                        img_elem = product_container.find('img')
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                        
                        # Get brand
                        brand_elem = product_container.select_one("[data-test='brand']") or product_container.select_one(".brand")
                        if brand_elem:
                            brand = brand_elem.get_text(strip=True)
                    
                    product_data = {
                        "name": name,
                        "url": link,
                        "price": price,
                        "image": image_url,
                        "brand": brand,
                        "availability": availability,
                        "is_presale": is_presale,
                        "retailer": "Currys",
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    products.append(product_data)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue
    
    # Remove duplicates based on product name and URL
    seen = set()
    unique_list = []
    for product in products:
        identifier = (product['name'], product['url'])
        if identifier not in seen:
            seen.add(identifier)
            unique_list.append(product)
    
    products = unique_list
    return products

def extract_numeric_price(price_text):
    """Extract numeric price from price text"""
    if not price_text or price_text == "Price not found":
        return None
    
    # Remove currency symbols and extract numbers
    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
    return float(price_match.group()) if price_match else None

def filter_presales(products):
    """Filter products to show only presales"""
    return [product for product in products if product.get('is_presale', False)]

def filter_by_price_range(products, min_price=None, max_price=None):
    """Filter products by price range"""
    filtered = []
    for product in products:
        numeric_price = extract_numeric_price(product.get('price'))
        if numeric_price is None:
            continue
        
        if min_price and numeric_price < min_price:
            continue
        if max_price and numeric_price > max_price:
            continue
        
        filtered.append(product)
    
    return filtered

def save_products_to_json(products, filename="scraped_products.json"):
    """Save products to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(products)} products to {filename}")

def save_products_to_csv(products, filename="scraped_products.csv"):
    """Save products to CSV file"""
    import csv
    
    if not products:
        print("No products to save")
        return
    
    fieldnames = products[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    
    print(f"Saved {len(products)} products to {filename}")

def print_product_summary(products):
    """Print summary of scraped products"""
    print(f"\n=== PRODUCT SCRAPING SUMMARY ===")
    print(f"Total products found: {len(products)}")
    
    # Count by retailer
    retailers = {}
    presales_count = 0
    
    for product in products:
        retailer = product.get('retailer', 'Unknown')
        retailers[retailer] = retailers.get(retailer, 0) + 1
        
        if product.get('is_presale', False):
            presales_count += 1
    
    print(f"Presales found: {presales_count}")
    print(f"Regular products: {len(products) - presales_count}")
    
    for retailer, count in retailers.items():
        print(f"{retailer}: {count} products")
    
    print("=" * 35)

def main():
    """Main function to run the complete scraper"""
    print("Starting enhanced retailer scraper...")
    print("Scraping Argos products...")
    
    # Get all products
    argos_products = get_argos_products()
    print(f"Found {len(argos_products)} Argos products")
    
    print("Scraping Currys products...")
    currys_products = get_currys_products()
    print(f"Found {len(currys_products)} Currys products")
    
    # Combine all products
    all_products = argos_products + currys_products
    
    # Print summary
    print_product_summary(all_products)
    
    # Save all products
    save_products_to_json(all_products, "all_products.json")
    save_products_to_csv(all_products, "all_products.csv")
    
    # Filter and save presales only
    presales = filter_presales(all_products)
    if presales:
        save_products_to_json(presales, "presales_only.json")
        save_products_to_csv(presales, "presales_only.csv")
        print(f"Saved {len(presales)} presale products separately")
    
    # Show sample of products
    print(f"\n=== SAMPLE PRODUCTS ===")
    for i, product in enumerate(all_products[:5]):
        status = "PRESALE" if product.get('is_presale') else "REGULAR"
        print(f"{i+1}. [{status}] {product['name']}")
        print(f"   Retailer: {product['retailer']}")
        print(f"   Price: {product['price']}")
        print(f"   Availability: {product['availability']}")
        print(f"   URL: {product['url']}")
        print("-" * 60)
    
    if presales:
        print(f"\n=== PRESALE PRODUCTS ===")
        for i, product in enumerate(presales[:3]):
            print(f"{i+1}. {product['name']}")
            print(f"   Retailer: {product['retailer']}")
            print(f"   Price: {product['price']}")
            print(f"   Availability: {product['availability']}")
            print(f"   URL: {product['url']}")
            print("-" * 60)
    
    return all_products

if __name__ == "__main__":
    products = main()
