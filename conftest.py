import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.rate_limit import limiter


@pytest.fixture(autouse=True)
def reset_state():
    limiter.reset()
    get_settings.cache_clear()
    yield
    limiter.reset()
    get_settings.cache_clear()


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def learner_headers(client):
    response = client.post(
        "/api/auth/login", json={"username": "learner", "password": "LearnerPass!2026"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
