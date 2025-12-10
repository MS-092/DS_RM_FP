import pytest
import asyncio
from httpx import AsyncClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root endpoint returns welcome message."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to GitForge Distributed System"}

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

@pytest.mark.asyncio
async def test_readiness_probe(client):
    """Test Kubernetes readiness probe."""
    response = await client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True}

@pytest.mark.asyncio
async def test_liveness_probe(client):
    """Test Kubernetes liveness probe."""
    response = await client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json() == {"alive": True}
