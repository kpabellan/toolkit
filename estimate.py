import pandas as pd
from collections import defaultdict
from datetime import datetime
import re

file_name = input("Enter inventory date (mm-dd-yy): ") + ".txt"

# Read raw lines to get the "As Of" date
with open(file_name, "r") as f:
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

# Load file into DataFrame
df = pd.read_csv(file_name, sep="\t", header=None, engine="python")

# Category mapping
category_keywords = {
    "ORGSTRAWB": ["orgstrawb", "orgstrwb", "orgstraw", "org straw"],
    "STRAWB": ["strawberry", "strawb", "strwb"],
    "HYDROBERRY": ["hydroberry"],
    "ORGBLUE": ["opblueorg", "orgblue"],
    "BLUE": ["opbluebrry", "blueberry", "bluebrry", "blue"],
    "ORGBLACK": ["orgblack", "orgblack"],
    "BLCKBRRY": ["blackberry", "opblckbrry", "blckbrry", "black", "blck"],
    "MISCORGRAS": ["miscorgras"],
    "ORGRASP": ["orgrasp"],
    "MISCRASP": ["miscrasp"],
    "RASP": ["raspberry", "rasp"]
}

def get_category(product_name):
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword.lower() in product_name.lower():
                return category
    return None

def clean_variety(product_name, fruit_category):
    keywords = category_keywords.get(fruit_category, [])
    variety = product_name
    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        variety = pattern.sub("", variety)
    # Strip whitespace and quotes
    return variety.strip().strip('"')

# Collect estimates
estimates = []

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
            estimate = int(str(data_row[1]).replace(",", "")) if pd.notna(data_row[1]) else 0
            if estimate > 0:
                variety = clean_variety(product_name, category)
                estimates.append((category, variety, estimate))
        except ValueError:
            pass

    i += 2

# Report
print(f"\nFruit Estimate Report as of {formatted_date}")
print(f"{'Fruit Category':<15} {'Variety':<60} {'CTN':>10}")
print("-" * 90)
for category, variety, estimate in estimates:
    print(f"{category:<15} {variety:<60} {estimate:>10}")
