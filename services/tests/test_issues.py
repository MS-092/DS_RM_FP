import pytest
from httpx import AsyncClient
from main import app
from database import Base, engine

@pytest.fixture(scope="function")
async def test_db():
    """Create test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_issue(client, test_db):
    """Test creating a new issue."""
    issue_data = {
        "title": "Test Issue",
        "description": "This is a test issue",
        "repository": "test-repo",
        "created_by": "test-user"
    }
    
    response = await client.post("/api/issues", json=issue_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == issue_data["title"]
    assert data["description"] == issue_data["description"]
    assert data["repository"] == issue_data["repository"]
    assert data["created_by"] == issue_data["created_by"]
    assert data["status"] == "open"
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_list_issues(client, test_db):
    """Test listing all issues."""
    # Create test issues
    for i in range(3):
        await client.post("/api/issues", json={
            "title": f"Test Issue {i}",
            "description": f"Description {i}",
            "repository": "test-repo",
            "created_by": "test-user"
        })
    
    # List issues
    response = await client.get("/api/issues")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert all("title" in issue for issue in data)

@pytest.mark.asyncio
async def test_get_issue(client, test_db):
    """Test getting a specific issue."""
    # Create an issue
    create_response = await client.post("/api/issues", json={
        "title": "Test Issue",
        "description": "Test Description",
        "repository": "test-repo",
        "created_by": "test-user"
    })
    issue_id = create_response.json()["id"]
    
    # Get the issue
    response = await client.get(f"/api/issues/{issue_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == issue_id
    assert data["title"] == "Test Issue"

@pytest.mark.asyncio
async def test_get_nonexistent_issue(client, test_db):
    """Test getting a non-existent issue returns 404."""
    response = await client.get("/api/issues/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_issue(client, test_db):
    """Test deleting an issue."""
    # Create an issue
    create_response = await client.post("/api/issues", json={
        "title": "Test Issue",
        "description": "Test Description",
        "repository": "test-repo",
        "created_by": "test-user"
    })
    issue_id = create_response.json()["id"]
    
    # Delete the issue
    response = await client.delete(f"/api/issues/{issue_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = await client.get(f"/api/issues/{issue_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_issue(client, test_db):
    """Test deleting a non-existent issue returns 404."""
    response = await client.delete("/api/issues/99999")
    assert response.status_code == 404
