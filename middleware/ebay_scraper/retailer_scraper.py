import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_argos_products():
    url = "https://www.argos.co.uk/category/3300986/smart-tech/"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    products = []

    for item in soup.select("div.ProductCardstyles__Title-sc-__sc-1v7bzit-6"):  # Adjust this if broken
        name = item.get_text(strip=True)
        link = "https://www.argos.co.uk" + item.find_parent("a")["href"]
        price_tag = item.find_parent("article").select_one("div.ProductCardPrice__Price")
        try:
            price = float(price_tag.get_text(strip=True).replace("£", ""))
        except:
            price = 0.0
        products.append({"name": name, "url": link, "price": price})
    return products

def get_currys_products():
    url = "https://www.currys.co.uk/smart-tech"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    products = []

    for item in soup.select("a.product-title-link"):
        name = item.get_text(strip=True)
        link = "https://www.currys.co.uk" + item["href"]
        price_tag = item.find_next("div", class_="product-price")
        try:
            price = float(price_tag.get_text(strip=True).replace("£", ""))
        except:
            price = 0.0
        products.append({"name": name, "url": link, "price": price})
    return products
