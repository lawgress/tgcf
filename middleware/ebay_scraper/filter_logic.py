def calculate_profit(retail_price, resale_prices):
    if not resale_prices:
        return None
    avg_resale = sum(resale_prices) / len(resale_prices)
    profit = avg_resale - retail_price
    if avg_resale > 2 * retail_price:
        return round(profit, 2)
    return None
