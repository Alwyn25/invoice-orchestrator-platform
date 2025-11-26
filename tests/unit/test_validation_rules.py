import pytest
from backend.agents.validation_agent.server import validate_gstin, validate_date

def test_validate_gstin():
    assert validate_gstin("29AAFCD5862R1Z5") == True
    assert validate_gstin("29AAFCD5862R1Z") == False
    assert validate_gstin(None) == False

def test_validate_date():
    assert validate_date("2025-11-25") == True
    assert validate_date("2099-12-31") == False
    assert validate_date("invalid-date") == False
    assert validate_date(None) == False
