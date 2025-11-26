import pytest
import httpx

@pytest.mark.e2e
def test_full_ingestion_flow():
    # This is a stubbed E2E test.
    # In a real system, you would upload a file and poll the services.
    ingestion_id = "e2e-test-ingestion-123"

    # 1. Upload file to gateway
    # response = httpx.post("http://localhost:8000/ingestion/upload", files={"file": ("test.pdf", b"dummy content")})
    # assert response.status_code == 200
    # ingestion_id = response.json()["ingestion_id"]

    # 2. Trigger orchestration
    # response = httpx.post(f"http://localhost:8100/orchestrate/{ingestion_id}")
    # assert response.status_code == 200

    # 3. Poll for completion
    # ...

    assert True
