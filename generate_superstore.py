"""
generate_superstore.py
Run this ONCE to create superstore.csv if you don't already have it.
Usage: python generate_superstore.py
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

REGIONS      = ["East", "West", "Central", "South"]
CATEGORIES   = {
    "Technology":       ["Phones", "Computers", "Monitors", "Accessories"],
    "Furniture":        ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies":  ["Binders", "Paper", "Storage", "Art", "Labels", "Fasteners"],
}
SEGMENTS     = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES   = ["Standard Class", "Second Class", "First Class", "Same Day"]
STATES = {
    "East":    ["New York", "Pennsylvania", "Ohio", "Virginia", "Florida"],
    "West":    ["California", "Washington", "Colorado", "Oregon", "Nevada"],
    "Central": ["Texas", "Illinois", "Michigan", "Minnesota", "Missouri"],
    "South":   ["Georgia", "North Carolina", "Tennessee", "Alabama", "Louisiana"],
}

first_names = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda",
               "William","Barbara","David","Susan","Richard","Jessica","Joseph","Sarah"]
last_names  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
               "Wilson","Anderson","Taylor","Thomas","Jackson","White","Harris","Martin"]

start = datetime(2014, 1, 1)
end   = datetime(2017, 12, 31)

rows = []
order_counter = 1

for _ in range(9994):
    order_date = start + timedelta(days=random.randint(0, (end - start).days))
    ship_date  = order_date + timedelta(days=random.randint(1, 7))
    region     = random.choice(REGIONS)
    category   = random.choices(
        list(CATEGORIES.keys()), weights=[0.35, 0.32, 0.33]
    )[0]
    sub_cat    = random.choice(CATEGORIES[category])
    segment    = random.choices(SEGMENTS, weights=[0.52, 0.30, 0.18])[0]
    ship_mode  = random.choices(SHIP_MODES, weights=[0.60, 0.19, 0.15, 0.06])[0]

    # Sales with category-dependent distribution
    if category == "Technology":
        base_sales = np.random.lognormal(mean=5.5, sigma=1.2)
    elif category == "Furniture":
        base_sales = np.random.lognormal(mean=5.2, sigma=1.0)
    else:
        base_sales = np.random.lognormal(mean=4.0, sigma=1.1)

    base_sales = np.clip(base_sales, 5, 5000)
    quantity   = random.choices([1, 2, 3, 4, 5, 6, 7], weights=[40, 25, 15, 8, 6, 4, 2])[0]
    discount   = random.choices([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                                weights=[35, 20, 18, 10, 7, 4, 3, 2, 1])[0]
    sales      = round(base_sales * quantity * (1 - discount), 2)

    # Profit margin varies by category and discount
    base_margin = {"Technology": 0.18, "Furniture": 0.12, "Office Supplies": 0.22}[category]
    margin      = base_margin - discount * 1.4 + np.random.normal(0, 0.05)
    profit      = round(sales * margin, 2)

    fname = random.choice(first_names)
    lname = random.choice(last_names)
    cust_id = f"CU-{random.randint(10000,99999)}"

    rows.append({
        "Row ID":       _ + 1,
        "Order ID":     f"CA-{order_date.year}-{order_counter:06d}",
        "Order Date":   order_date.strftime("%Y-%m-%d"),
        "Ship Date":    ship_date.strftime("%Y-%m-%d"),
        "Ship Mode":    ship_mode,
        "Customer ID":  cust_id,
        "Customer Name": f"{fname} {lname}",
        "Segment":      segment,
        "Country":      "United States",
        "City":         random.choice(STATES[region]),
        "State":        random.choice(STATES[region]),
        "Postal Code":  random.randint(10000, 99999),
        "Region":       region,
        "Product ID":   f"PRD-{random.randint(1000,9999)}",
        "Category":     category,
        "Sub-Category": sub_cat,
        "Product Name": f"{sub_cat} Model {random.randint(100,999)}",
        "Sales":        sales,
        "Quantity":     quantity,
        "Discount":     discount,
        "Profit":       profit,
    })
    order_counter += 1

df = pd.DataFrame(rows)
df.to_csv("superstore.csv", index=False)
print(f"✅ superstore.csv created with {len(df):,} rows")
print(df.head())