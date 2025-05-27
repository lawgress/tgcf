import requests
from bs4 import BeautifulSoup
import time
import random

def get_argos_products():
    """Enhanced Argos product scraper to grab more products"""
    products = []
    
    # Multiple category URLs to scrape more products
    urls = [
        "https://www.argos.co.uk/category/33000986/smart-tech/",
        "https://www.argos.co.uk/category/33006/technology/",
        "https://www.argos.co.uk/category/33007/laptops-and-pcs/",
        "https://www.argos.co.uk/category/33008/mobile-phones-and-accessories/",
        "https://www.argos.co.uk/category/33013/tablets-and-ereaders/"
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
                        "retailer": "Argos"
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
    """Enhanced Currys product scraper to grab more products"""
    products = []
    
    # Multiple category URLs to scrape more products
    urls = [
        "https://www.currys.co.uk/smart-tech",
        "https://www.currys.co.uk/computing",
        "https://www.currys.co.uk/computing/laptops",
        "https://www.currys.co.uk/phones-broadband-and-sat-nav/mobile-phones",
        "https://www.currys.co.uk/computing/tablets-and-ereaders",
        "https://www.currys.co.uk/gaming",
        "https://www.currys.co.uk/cameras-and-camcorders"
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
                        "retailer": "Currys"
                    }
                    
                    products.append(product_data)
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue
    
    # Remove duplicates based on product name and URL
    seen = set()
    unique_products = []
    for product in products:
        identifier = (product['name'], product['url'])
        if identifier not in seen:
            seen.add(identifier)
            unique_products.append(product)
    
    return filtered_products
