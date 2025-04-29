from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate


def test_create_user(client: TestClient, db: AsyncSession) -> None:
    """Test creating a user."""
    user_in = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User",
    )
    
    response = client.post("/api/v1/users/", json=user_in.model_dump())
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_in.email
    assert data["full_name"] == user_in.full_name
    assert "id" in data


def test_get_user(client: TestClient, db: AsyncSession, test_user: User) -> None:
    """Test getting a user by ID."""
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert data["id"] == test_user.id


def test_list_users(client: TestClient, db: AsyncSession, test_user: User) -> None:
    """Test listing users."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == test_user.email
    assert data[0]["full_name"] == test_user.full_name
    assert data[0]["id"] == test_user.id


def test_update_user(client: TestClient, db: AsyncSession, test_user: User) -> None:
    """Test updating a user."""
    user_update = {
        "full_name": "Updated Name",
        "email": "updated@example.com",
    }
    
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json=user_update,
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user_update["email"]
    assert data["full_name"] == user_update["full_name"]
    assert data["id"] == test_user.id


def test_delete_user(client: TestClient, db: AsyncSession, test_user: User) -> None:
    """Test deleting a user."""
    response = client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 204
    
    # Verify user is deleted
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 404 