"""Digital Asset Links for the Play Store TWA."""

from fastapi.testclient import TestClient

from sentinel_suisse.config import get_settings
from sentinel_suisse.main import create_app


def test_assetlinks_empty_without_fingerprint(client: TestClient) -> None:
    trusted_hosts = get_settings().trusted_hosts_list()
    host_header = trusted_hosts[0] if trusted_hosts else "testserver"
    response = client.get("/.well-known/assetlinks.json", headers={"Host": host_header})
    assert response.status_code == 200
    assert response.json() == []


def test_assetlinks_includes_package_and_normalized_fingerprint(monkeypatch) -> None:
    monkeypatch.setenv("ANDROID_PACKAGE_ID", "ch.linkswiss.app")
    monkeypatch.setenv(
        "PLAY_ASSETLINKS_SHA256",
        "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
    )
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/.well-known/assetlinks.json")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    target = data[0]["target"]
    assert target["namespace"] == "android_app"
    assert target["package_name"] == "ch.linkswiss.app"
    assert target["sha256_cert_fingerprints"] == [
        "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:"
        "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
    ]
    get_settings.cache_clear()
