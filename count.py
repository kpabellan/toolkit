import pandas as pd
from collections import defaultdict
from datetime import datetime

# Read raw lines to get the "As Of" date
with open("daily.txt", "r") as f:
    lines = f.readlines()

# Split tab-separated rows for easy parsing
rows = [line.strip().split("\t") for line in lines]

# Extract the "As Of" date
as_of_date = "Unknown Date"
for row in rows:
    normalized = [cell.strip().replace('"', '') for cell in row]
    if "As Of:" in normalized:
        idx = normalized.index("As Of:")
        if idx + 2 < len(normalized):
            possible_date = normalized[idx + 2].strip()
            if possible_date:
                as_of_date = possible_date
        break

try:
    parsed_date = datetime.strptime(as_of_date, "%b %d, %Y %H:%M:%S")
except ValueError:
    try:
        parsed_date = datetime.strptime(as_of_date, "%b %d, %Y")
    except ValueError:
        parsed_date = None

formatted_date = parsed_date.strftime("%B %d, %Y") if parsed_date else as_of_date

# Load the same file into DataFrame
df = pd.read_csv("daily.txt", sep="\t", header=None, engine="python")

# Define category keywords
category_keywords = {
    "Blackberry": ["Blckbrry", "Black", "Blck"],
    "Blueberry": ["Bluebrry", "Blue"],
    "Raspberry": ["Rasp", "Raspberry"],
    "Strawberry": ["Strwb", "Strawberry"],
}

# Helper to classify
def get_category(product_name):
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword.lower() in product_name.lower():
                return category
    return None

# Aggregate totals
totals = defaultdict(lambda: {"Received": 0, "Shipped": 0})

i = 0
while i < len(df) - 1:
    product_row = df.iloc[i]
    data_row = df.iloc[i + 1]

    product_name = str(product_row[0]).strip()
    if not product_name or product_name.startswith("Qnt On") or "Estimate" in product_name:
        i += 1
        continue

    category = get_category(product_name)
    if category:
        try:
            received = int(str(data_row[4]).replace(",", "")) if pd.notna(data_row[4]) else 0
            shipped = int(str(data_row[5]).replace(",", "")) if pd.notna(data_row[5]) else 0
            totals[category]["Received"] += received
            totals[category]["Shipped"] += shipped
        except ValueError:
            pass

    i += 2

# Print final report
print(f"Fruit Inventory Report as of {formatted_date}")
print(f"{'Fruit Category':<15} {'Received':>10} {'Shipped':>10}")
print("-" * 40)
for category, values in totals.items():
    print(f"{category:<15} {values['Received']:>10} {values['Shipped']:>10}")
