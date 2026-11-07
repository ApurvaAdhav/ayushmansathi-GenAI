import json
import pandas as pd
from pathlib import Path

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load records
DATA_FILE = BASE_DIR / "data" / "records.json"

with open(DATA_FILE, "r", encoding="utf-8") as file:
    records = json.load(file)

# Convert records into DataFrame
df = pd.DataFrame(records)

# Fact 1: Total records
print("Total records:", len(df))

# Fact 2: Records by topic
print("\nRecords by topic:")
print(df["rule_topic"].value_counts().head())

# Fact 3: Unique documents
print("\nNumber of unique documents:", df["document_title"].nunique())
