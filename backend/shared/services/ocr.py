from typing import List, Dict

class OcrService:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client

    def perform_ocr(self, file_bytes: bytes, file_name: str) -> str:
        """
        Performs OCR on a file using a cascading series of OCR services.
        This is a stub and returns fake OCR text.
        """
        # In a real implementation, you would call the OCR services in order:
        # 1. Typhoon
        # 2. GPT-4 Vision
        # 3. Azure Document Intelligence
        # 4. Tesseract
        # 5. EasyOCR

        # For now, we'll return a fake result.
        return "Invoice Number: INV-123\nDate: 2025-11-25\nTotal: 100.00"

def get_ocr_service(mcp_client) -> OcrService:
    return OcrService(mcp_client)
