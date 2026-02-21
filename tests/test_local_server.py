from app.local_server import _parse_cookie


def test_parse_cookie_empty():
    assert _parse_cookie(None) == {}


def test_parse_cookie_pairs():
    cookies = _parse_cookie("qx_session=abc123; theme=dark")
    assert cookies["qx_session"] == "abc123"
    assert cookies["theme"] == "dark"
