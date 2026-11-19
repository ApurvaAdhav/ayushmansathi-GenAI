from app.records import count_by, get_by_id, load_records, search
from app.smart_search import smart_search

# Sample records for testing
sample_records = [
    {
        "id": 1,
        "rule_topic": "Dental",
        "rule_text": "Dental treatment is covered under the scheme."
    },
    {
        "id": 2,
        "rule_topic": "Hospitalization",
        "rule_text": "Hospital admission is covered under the scheme."
    },
    {
        "id": 3,
        "rule_topic": "Dental",
        "rule_text": "Dental procedures have specific conditions."
    }
]


# Test 1: Load records
def test_load_records():
    records = load_records()
    assert isinstance(records, list)
    assert len(records) > 0


# Test 2: Search by topic
def test_search_by_topic():
    results = search(sample_records, "Dental")
    assert len(results) == 2


# Test 3: Search by text
def test_search_by_text():
    results = search(sample_records, "specific conditions")
    assert len(results) == 1


# Test 4: Search with no matching keyword
def test_search_no_match():
    results = search(sample_records, "Cancer")
    assert len(results) == 0


# Test 5: Count records by category
def test_count_by_category():
    count = count_by(sample_records, "Dental")
    assert count == 2


# Test 6: Get record by ID
def test_get_by_id():
    record = get_by_id(sample_records, 2)
    assert record["rule_topic"] == "Hospitalization"


# Test 7: Get non-existing record
def test_get_by_invalid_id():
    record = get_by_id(sample_records, 10)
    assert record is None


# Test 8: Search is case-insensitive
def test_search_case_insensitive():
    results = search(sample_records, "dental")
    assert len(results) == 2


# Test 9: Smart search returns relevant records
def test_smart_search():
    results = smart_search("dental treatment")

    assert len(results) > 0
    assert "similarity_score" in results[0]


# Test 10: Smart search returns an empty list for blank query
def test_smart_search_empty_query():
    results = smart_search("   ")

    assert results == []


# Test 11: Smart search returns no results for unrelated query
def test_smart_search_no_match():
    results = smart_search("xyzabc123")

    assert results == []


# Test 12: Smart search respects top_k
def test_smart_search_top_k():
    results = smart_search("hospital treatment", top_k=2)

    assert len(results) <= 2
