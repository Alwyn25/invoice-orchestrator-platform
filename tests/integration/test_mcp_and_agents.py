import pytest
from backend.shared.clients.mcp import MCPClient
from backend.shared.clients.agents import AgentsClient

@pytest.mark.integration
def test_mcp_save_and_get_document():
    mcp_client = MCPClient()
    ingestion_id = "test-ingestion-123"
    file_name = "test.pdf"
    file_url = "s3://dummy/test.pdf"
    metadata = {"source": "test"}

    mcp_client.save_document(ingestion_id, file_name, file_url, metadata)
    doc = mcp_client.get_document(ingestion_id)

    assert doc is not None
    assert doc.doc_ref == ingestion_id

@pytest.mark.integration
def test_extraction_agent_ocr():
    agents_client = AgentsClient()
    ingestion_id = "test-ingestion-456"
    file_url = "/tmp/dummy.pdf" # This will fail if the file doesn't exist
    metadata = {}

    # Create a dummy file for the test
    with open(file_url, "w") as f:
        f.write("dummy content")

    response = agents_client.start_ocr(ingestion_id, file_url, metadata)
    assert response.status == "EXTRACTED"
