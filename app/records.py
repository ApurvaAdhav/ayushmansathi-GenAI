from data.sample_records import records

# Load all healthcare records
def load_records():
    return records


# Search records by keyword
def search(records, keyword):
    results = []

    for record in records:
        if (keyword.lower() in record["rule_topic"].lower()
                or keyword.lower() in record["rule_text"].lower()):
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