import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify the API is online and using the correct engine."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["engine"] == "Groq + HuggingFace"

@pytest.mark.asyncio
async def test_health_check():
    """Verify the health endpoint returns success."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_query_no_index():
    """Verify the API handles queries correctly when no document is indexed."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/query", json={"question": "What is in this PDF?"})
    # Should return 404 if load_vector_store returns None
    assert response.status_code == 404
    assert "No indexed document found" in response.json()["detail"]