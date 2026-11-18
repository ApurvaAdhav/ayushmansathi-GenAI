
from datetime import date

# Total annual family floater coverage
TOTAL_COVER = 500000

# Demo hospital claims for the current year
# Replace these sample entries with actual claim records when needed.
hospital_claims = [
    {
        "claim_id": 1,
        "hospital": "City Care Hospital",
        "amount": 75000,
        "date": f"{date.today().year}-02-15"
    },
    {
        "claim_id": 2,
        "hospital": "Sunrise Hospital",
        "amount": 50000,
        "date": f"{date.today().year}-05-20"
    }
]


def cover_balance_tracker(planned_package=0):
    """
    Calculate used and remaining family floater coverage.
    Check whether a planned hospital package exceeds the balance.
    """

    current_year = date.today().year

    # Calculate claims made during the current year
    used_amount = sum(
        claim["amount"]
        for claim in hospital_claims
        if date.fromisoformat(claim["date"]).year == current_year
    )

    remaining_amount = TOTAL_COVER - used_amount

    planned_package = max(0, planned_package)

    result = {
        "total_cover": TOTAL_COVER,
        "used_amount": used_amount,
        "remaining_amount": remaining_amount,
        "planned_package": planned_package,
        "warning": None
    }

    if planned_package > remaining_amount:
        result["warning"] = (
            "Warning: The planned package exceeds the remaining "
            "family floater coverage."
        )
    else:
        result["warning"] = (
            "The planned package is within the remaining coverage."
        )

    return result


def add_hospital_claim(hospital, amount, claim_date=None):
    """Add a new hospital claim to the claim list."""

    if amount <= 0:
        raise ValueError("Claim amount must be greater than zero.")

    claim_date = claim_date or date.today().isoformat()

    claim = {
        "claim_id": len(hospital_claims) + 1,
        "hospital": hospital,
        "amount": amount,
        "date": claim_date
    }

    hospital_claims.append(claim)

    return claim


if __name__ == "__main__":

    result = cover_balance_tracker(planned_package=400000)

    print("Family Floater Cover Tracker")
    print("----------------------------")
    print("Total Cover:", result["total_cover"])
    print("Used Amount:", result["used_amount"])
    print("Remaining Amount:", result["remaining_amount"])
    print("Planned Package:", result["planned_package"])
    print(result["warning"])
