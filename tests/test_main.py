import pytest
from httpx import AsyncClient, ASGITransport
from main import app, ScrapeRequest

@pytest.mark.asyncio
async def test_scrape_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/scrape", json={"url": "https://example.com"})
    data = resp.json()
    assert data["success"] is True
    assert data["title"] is not None

def test_scrape_failure_invalid_url():
    transport = ASGITransport(app=app)
    async def run_test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/scrape", json={"url": "http://invalid-local-host-that-does-not-exist"})
        return resp.json()
    import asyncio
    data = asyncio.run(run_test())
    assert data["success"] is False
    assert data["error"] is not None

def test_scrape_missing_url():
    transport = ASGITransport(app=app)
    async def run_test():
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/scrape", json={})
        return resp.status_code
    import asyncio
    status = asyncio.run(run_test())
    assert status == 422