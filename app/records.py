import json
from pathlib import Path

# Path to the extracted healthcare records
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


# Load all healthcare records
def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    for index, record in enumerate(records, start=1):
        record["id"] = index

    return records


# Search records by keyword
def search(records, keyword):
    results = []

    for record in records:
        if (
            keyword.lower() in record["rule_topic"].lower()
            or keyword.lower() in record["rule_text"].lower()
        ):
            results.append(record)

    return results


# Count records by category
def count_by(records, category):
    count = 0

    for record in records:
        if record["rule_topic"].lower() == category.lower():
            count += 1

    return count


# Get a record by ID
def get_by_id(records, record_id):
    for record in records:
        if record["id"] == record_id:
            return record

    return None
