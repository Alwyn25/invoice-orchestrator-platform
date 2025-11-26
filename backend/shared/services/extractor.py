import json
from backend.shared.prompts import EXTRACTION_SCHEMA_PROMPT

class ExtractorService:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client

    def extract_schema(self, ocr_text: str) -> dict:
        """
        Extracts a structured schema from raw OCR text using an LLM.
        """
        prompt = EXTRACTION_SCHEMA_PROMPT.format(extracted_text=ocr_text)

        # In a real implementation, you would call the MCP's QueryLLM RPC.
        # For now, we'll return a fake result.
        fake_llm_response = {
            "invoiceNumber": "INV-123",
            "invoiceDate": "2025-11-25",
            "dueDate": None,
            "vendor": {"name": "Dummy Vendor", "gstin": None, "pan": None, "address": None},
            "customer": {"name": "Dummy Customer", "address": None},
            "lineItems": [],
            "totals": {"subtotal": 100.0, "gstAmount": 0.0, "roundOff": None, "grandTotal": 100.0},
            "paymentDetails": {"mode": None, "reference": None, "status": None},
        }

        # llm_response = self.mcp_client.query_llm(prompt)
        # return json.loads(llm_response.text)

        return fake_llm_response

def get_extractor_service(mcp_client) -> ExtractorService:
    return ExtractorService(mcp_client)
