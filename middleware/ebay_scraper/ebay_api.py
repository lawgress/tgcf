import requests
import os

EBAY_APP_ID = os.getenv("EBAY_APP_ID")

def get_ebay_resale_data(query):
    headers = {"Authorization": f"Bearer {EBAY_APP_ID}"}
    params = {
        "q": query,
        "limit": 10,
        "sort": "-price",
        "filter": "price:[5..100000]",
        "fieldgroups": "ASPECT_REFINEMENTS"
    }
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    sold_prices = [float(item['price']['value']) for item in data.get('itemSummaries', [])]
    return sold_prices if sold_prices else []


