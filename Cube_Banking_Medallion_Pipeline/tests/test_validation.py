import pytest

def validate_transaction(row):
    if float(row["amount"]) <= 0:
        raise ValueError("amount must be positive")
    if row["status"] not in {"SUCCESS","FAILED","PENDING"}:
        raise ValueError("invalid status")
    return True

def test_valid_transaction():
    assert validate_transaction({"amount":"100.50","status":"SUCCESS"})

def test_negative_amount_rejected():
    with pytest.raises(ValueError,match="positive"):
        validate_transaction({"amount":"-1","status":"SUCCESS"})

def test_invalid_status_rejected():
    with pytest.raises(ValueError,match="invalid status"):
        validate_transaction({"amount":"5","status":"UNKNOWN"})
