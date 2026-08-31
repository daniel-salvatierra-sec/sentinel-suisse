"""Public in-app listing translation."""

from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient


def _gtx_payload(translated: str) -> list:
    return [[[translated, "orig", None, None, 0]]]


def test_public_translate_returns_title_and_body(client: TestClient) -> None:
    fake = MagicMock()
    fake.raise_for_status = MagicMock()
    fake.json.side_effect = [
        _gtx_payload("Camarero en Annemasse"),
        _gtx_payload("Contrato indefinido, 100%."),
    ]

    with patch("sentinel_suisse.services.public_translate.httpx.get", return_value=fake):
        response = client.post(
            "/api/v1/public/translate",
            json={
                "lang": "es",
                "title": "Serveur à Annemasse",
                "body": "CDI, 100%.",
            },
        )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "title": "Camarero en Annemasse",
        "body": "Contrato indefinido, 100%.",
    }


def test_public_translate_keeps_original_when_upstream_fails(client: TestClient) -> None:
    with patch(
        "sentinel_suisse.services.public_translate.httpx.get",
        side_effect=httpx.ConnectError("down"),
    ):
        response = client.post(
            "/api/v1/public/translate",
            json={"lang": "pt", "title": "Serveur", "body": "CDI"},
        )

    assert response.status_code == 200, response.text
    assert response.json() == {"title": "Serveur", "body": "CDI"}


def test_public_translate_rejects_unknown_lang(client: TestClient) -> None:
    response = client.post(
        "/api/v1/public/translate",
        json={"lang": "it", "title": "Hello", "body": ""},
    )
    assert response.status_code == 422
