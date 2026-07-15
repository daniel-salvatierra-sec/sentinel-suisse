"""Deep-link query shape for QR subscribe (Phase 22, mirrored for docs/CI)."""


def test_subscribe_query_shape() -> None:
    # Frontend builds: /?tab=account&lang=fr&type=housing&q=Geneva
    from urllib.parse import parse_qs, urlparse

    url = "http://127.0.0.1:5173/?tab=account&lang=fr&type=housing&q=Geneva"
    qs = parse_qs(urlparse(url).query)
    assert qs["tab"] == ["account"]
    assert qs["lang"] == ["fr"]
    assert qs["type"] == ["housing"]
    assert qs["q"] == ["Geneva"]
