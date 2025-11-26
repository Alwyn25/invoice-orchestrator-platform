import pytest
from backend.agents.conversion_agent.server import to_tally_xml, to_zoho_json

def test_to_tally_xml():
    schema = {"invoice_number": "INV-123"}
    xml = to_tally_xml(schema)
    assert "<VOUCHERNUMBER>INV-123</VOUCHERNUMBER>" in xml

def test_to_zoho_json():
    schema = {"invoice_number": "INV-123", "invoice_date": "2025-11-25", "grand_total": 100.00}
    zoho_json = to_zoho_json(schema)
    assert zoho_json["invoice_number"] == "INV-123"
    assert zoho_json["total"] == 100.00
