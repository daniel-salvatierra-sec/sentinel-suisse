"""AI assistant (free-form chat) endpoint tests."""

from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient


def test_assistant_config_disabled_by_default(client: TestClient) -> None:
    response = client.get("/api/v1/assistant/config")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is False
    assert body["max_input_chars"] > 0


def test_assistant_chat_returns_503_when_disabled(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Bonjour", "lang": "fr"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "assistant_disabled"


def test_assistant_chat_success(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    fake_response = MagicMock()
    fake_response.raise_for_status = MagicMock()
    fake_response.json.return_value = {
        "choices": [{"message": {"content": "Bonjour ! Comment puis-je aider ?"}}]
    }

    with patch(
        "sentinel_suisse.services.assistant.httpx.post", return_value=fake_response
    ) as mock_post:
        response = client.post(
            "/api/v1/assistant/chat",
            json={"message": "Comment fonctionne Premium ?", "lang": "fr"},
        )

    assert response.status_code == 200, response.text
    assert response.json()["reply"] == "Bonjour ! Comment puis-je aider ?"
    assert mock_post.called
    sent_payload = mock_post.call_args.kwargs["json"]
    assert sent_payload["messages"][0]["role"] == "system"
    assert sent_payload["messages"][-1] == {
        "role": "user",
        "content": "Comment fonctionne Premium ?",
    }

    get_settings.cache_clear()


def test_assistant_chat_upstream_error_returns_502(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    with patch(
        "sentinel_suisse.services.assistant.httpx.post",
        side_effect=httpx.ConnectError("boom"),
    ):
        response = client.post(
            "/api/v1/assistant/chat",
            json={"message": "Salut", "lang": "fr"},
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "assistant_upstream_error"

    get_settings.cache_clear()


def test_assistant_chat_rejects_empty_message(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()

    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "   ", "lang": "fr"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "empty_message"

    get_settings.cache_clear()
