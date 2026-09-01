import asyncio

from app.llm import MockLLMProvider, PromptEnvelope


def test_health_and_security_headers(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-security-policy"].startswith("default-src 'self'")


def test_valid_authentication_and_identity(client):
    login = client.post(
        "/api/auth/login", json={"username": "learner", "password": "LearnerPass!2026"}
    )
    assert login.status_code == 200
    identity = client.get(
        "/api/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )
    assert identity.json() == {"username": "learner", "role": "user"}


def test_invalid_authentication(client):
    response = client.post(
        "/api/auth/login", json={"username": "learner", "password": "incorrect-password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_chat_uses_mock(client, learner_headers):
    response = client.post("/api/chat", headers=learner_headers, json={"message": "hello"})
    assert response.status_code == 200
    assert response.json()["response"] == "Mock assistant received: hello"


def test_mock_provider_is_deterministic():
    provider = MockLLMProvider()
    prompt = PromptEnvelope("system", "context", "same")
    first = asyncio.run(provider.generate(prompt))
    second = asyncio.run(provider.generate(prompt))
    assert first == second
