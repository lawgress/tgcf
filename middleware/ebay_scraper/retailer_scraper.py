import requests
from bs4 import BeautifulSoup

def get_argos_products():
    url = "https://www.argos.co.uk/category/3300986/smart-tech/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    products = []
    for item in soup.select(".ProductCardstyles__Title-sc-__sc-1gqk1k7-10"):
        name = item.get_text(strip=True)
        link = "https://www.argos.co.uk" + item.parent['href']
        price = 50  # Placeholder price
        products.append({"name": name, "url": link, "price": price})
    return products

def get_currys_products():
    url = "https://www.currys.co.uk/smart-tech"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    products = []
    for item in soup.select("a.ProductCardstyles__Title"):
        name = item.get_text(strip=True)
        link = "https://www.currys.co.uk" + item['href']
        price = 60  # Placeholder price
        products.append({"name": name, "url": link, "price": price})
    return products
