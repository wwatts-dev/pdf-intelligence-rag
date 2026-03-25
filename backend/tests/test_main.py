import pytest
import os
import sys
from httpx import AsyncClient, ASGITransport

# This allows the test to "see" main.py in the directory above it
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Define the path to the test PDF
# Ensure this matches the internal container path /app/tests/test_docs/...
TEST_DOC_PATH = os.path.join(os.path.dirname(__file__), "test_docs", "empsit.pdf")

@pytest.mark.asyncio
async def test_upload_and_query():
    # Fix: Use ASGITransport for newer httpx versions
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # 1. Verify Health
        health = await ac.get("/health")
        assert health.status_code == 200
        
        # 2. Test PDF Upload
        if not os.path.exists(TEST_DOC_PATH):
            pytest.fail(f"Test PDF not found at {TEST_DOC_PATH}.")
            
        with open(TEST_DOC_PATH, "rb") as f:
            files = {"file": ("empsit.pdf", f, "application/pdf")}
            upload_resp = await ac.post("/upload", files=files)
        
        assert upload_resp.status_code == 200
        
        # 3. Test Directed Query (The '4.4 percent' check)
        query = {"question": "What was the unemployment rate in February 2026?"}
        query_resp = await ac.post("/query", json=query)
        
        assert query_resp.status_code == 200
        answer = query_resp.json().get("answer", "")
        sources = query_resp.json().get("sources", [])
        
        assert "4.4 percent" in answer
        assert "empsit.pdf" in sources