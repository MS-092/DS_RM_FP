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

@pytest.fixture
async def test_issue(client, test_db):
    """Create a test issue for comment tests."""
    response = await client.post("/api/issues", json={
        "title": "Test Issue for Comments",
        "description": "Test Description",
        "repository": "test-repo",
        "created_by": "test-user"
    })
    return response.json()

@pytest.mark.asyncio
async def test_create_comment(client, test_db, test_issue):
    """Test creating a comment on an issue."""
    comment_data = {
        "issue_id": test_issue["id"],
        "user": "commenter",
        "body": "This is a test comment"
    }
    
    response = await client.post("/api/comments", json=comment_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["issue_id"] == comment_data["issue_id"]
    assert data["user"] == comment_data["user"]
    assert data["body"] == comment_data["body"]
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_get_comments_for_issue(client, test_db, test_issue):
    """Test getting all comments for an issue."""
    issue_id = test_issue["id"]
    
    # Create multiple comments
    for i in range(3):
        await client.post("/api/comments", json={
            "issue_id": issue_id,
            "user": f"user{i}",
            "body": f"Comment {i}"
        })
    
    # Get comments
    response = await client.get(f"/api/comments/issue/{issue_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3
    assert all(comment["issue_id"] == issue_id for comment in data)

@pytest.mark.asyncio
async def test_get_comments_for_nonexistent_issue(client, test_db):
    """Test getting comments for non-existent issue returns empty list."""
    response = await client.get("/api/comments/issue/99999")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_delete_comment(client, test_db, test_issue):
    """Test deleting a comment."""
    # Create a comment
    create_response = await client.post("/api/comments", json={
        "issue_id": test_issue["id"],
        "user": "test-user",
        "body": "Test comment"
    })
    comment_id = create_response.json()["id"]
    
    # Delete the comment
    response = await client.delete(f"/api/comments/{comment_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert response.json()["id"] == comment_id

@pytest.mark.asyncio
async def test_delete_nonexistent_comment(client, test_db):
    """Test deleting a non-existent comment returns 404."""
    response = await client.delete("/api/comments/99999")
    assert response.status_code == 404
