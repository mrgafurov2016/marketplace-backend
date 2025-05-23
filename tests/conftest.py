import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import conn


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def create_test_user(client):
    # Создаем тестового пользователя
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    })
    assert response.status_code in [200, 409]  # 409 если уже создан
    return {"email": "test@example.com", "password": "testpassword"}


@pytest.fixture(scope="module")
def token(client, create_test_user):
    # Получаем токен
    response = client.post("/auth/login", data={
        "username": create_test_user["email"],
        "password": create_test_user["password"]
    })
    assert response.status_code == 200
    return response.json()["access_token"]