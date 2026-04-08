import pytest
import os
import sys
import uuid # Added for generating test session IDs
from httpx import AsyncClient, ASGITransport

# This allows the test to "see" main.py in the directory above it
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Define the path to the test PDF
TEST_DOC_PATH = os.path.join(os.path.dirname(__file__), "test_docs", "empsit.pdf")

@pytest.mark.asyncio
async def test_stateful_rag_flow():
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
        
        # --- NEW: STATEFUL TESTING ---
        test_session_id = str(uuid.uuid4())

        # 3. Test Directed Query (Initial Question)
        query1 = {
            "question": "What was the unemployment rate in February 2026?",
            "session_id": test_session_id
        }
        query_resp1 = await ac.post("/query", json=query1)
        
        assert query_resp1.status_code == 200
        answer1 = query_resp1.json().get("answer", "")
        assert "4.4 percent" in answer1

        # 4. Test Conversational Memory (Follow-up Question)
        # We use a pronoun ("it") to see if the agent remembers the context
        query2 = {
            "question": "Is that higher or lower than the previous month?",
            "session_id": test_session_id
        }
        query_resp2 = await ac.post("/query", json=query2)
        
        assert query_resp2.status_code == 200
        answer2 = query_resp2.json().get("answer", "")
        standalone = query_resp2.json().get("standalone_query", "")

        # Logic Check: Did the LLM rewrite the query correctly?
        # It should have turned "that" into something related to the unemployment rate.
        assert len(standalone) > len(query2["question"]) 
        assert answer2 != "" 
        
        # 5. Verify Source Tracking
        sources = query_resp2.json().get("sources", [])
        assert "empsit.pdf" in sources