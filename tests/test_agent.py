
from app.tools import TOTAL_COVER, add_hospital_claim, cover_balance_tracker


# Test 1: Check total coverage
def test_total_cover():
    result = cover_balance_tracker()

    assert result["total_cover"] == TOTAL_COVER


# Test 2: Check used and remaining amount
def test_cover_balance():
    result = cover_balance_tracker()

    assert result["used_amount"] >= 0
    assert result["remaining_amount"] == (
        TOTAL_COVER - result["used_amount"]
    )


# Test 3: Planned package within remaining coverage
def test_package_within_coverage():
    result = cover_balance_tracker(planned_package=100000)

    assert "within the remaining coverage" in result["warning"]


# Test 4: Planned package exceeds remaining coverage
def test_package_exceeds_coverage():
    result = cover_balance_tracker(planned_package=500000)

    assert "exceeds the remaining" in result["warning"]


# Test 5: Negative planned package becomes zero
def test_negative_planned_package():
    result = cover_balance_tracker(planned_package=-1000)

    assert result["planned_package"] == 0


# Test 6: Add a hospital claim
def test_add_hospital_claim():
    claim = add_hospital_claim(
        hospital="Test Hospital",
        amount=1000,
        claim_date="2026-10-10"
    )

    assert claim["hospital"] == "Test Hospital"
    assert claim["amount"] == 1000
