def checkout(items, customer_type):
    total = 0
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if customer_type == "gold":
            discount = 0.20
        elif customer_type == "silver":
            discount = 0.10
        else:
            discount = 0.0
        line = price * qty
        line = line - line * discount
        total = total + line
    tax = total * 0.18
    total = total + tax
    return round(total, 2)


def preview(items, customer_type):
    total = 0
    for item in items:
        price = item["price"]
        qty = item["qty"]
        if customer_type == "gold":
            discount = 0.20
        elif customer_type == "silver":
            discount = 0.10
        else:
            discount = 0.0
        line = price * qty
        line = line - line * discount
        total = total + line
    return round(total, 2)
