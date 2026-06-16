"""Tests for link creation, redirection, analytics and ownership."""


def test_create_link_generates_code(client, auth_headers):
    res = client.post(
        "/links", json={"target_url": "https://example.com/page"}, headers=auth_headers
    )
    assert res.status_code == 201
    body = res.json()
    assert body["code"]
    assert body["short_url"].endswith(body["code"])
    assert body["clicks"] == 0


def test_create_link_with_custom_code(client, auth_headers):
    res = client.post(
        "/links",
        json={"target_url": "https://example.com", "code": "my-link"},
        headers=auth_headers,
    )
    assert res.status_code == 201
    assert res.json()["code"] == "my-link"


def test_duplicate_custom_code_conflicts(client, auth_headers):
    payload = {"target_url": "https://example.com", "code": "taken"}
    assert client.post("/links", json=payload, headers=auth_headers).status_code == 201
    assert client.post("/links", json=payload, headers=auth_headers).status_code == 409


def test_reserved_code_rejected(client, auth_headers):
    res = client.post(
        "/links",
        json={"target_url": "https://example.com", "code": "auth"},
        headers=auth_headers,
    )
    assert res.status_code == 400


def test_invalid_url_rejected(client, auth_headers):
    res = client.post(
        "/links", json={"target_url": "not-a-url"}, headers=auth_headers
    )
    assert res.status_code == 422


def test_list_links_returns_created(client, auth_headers):
    client.post(
        "/links", json={"target_url": "https://a.com", "code": "aaa"}, headers=auth_headers
    )
    client.post(
        "/links", json={"target_url": "https://b.com", "code": "bbb"}, headers=auth_headers
    )
    res = client.get("/links", headers=auth_headers)
    assert res.status_code == 200
    codes = {link["code"] for link in res.json()}
    assert {"aaa", "bbb"} <= codes


def test_redirect_and_analytics(client, auth_headers):
    res_create = client.post(
        "/links",
        json={"target_url": "https://example.com/target", "code": "goto"},
        headers=auth_headers,
    )
    assert res_create.status_code == 201

    # Redirect should 302 to the target.
    res = client.get("/goto", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "https://example.com/target"

    # The click is recorded via a background task and shows up in stats.
    stats = client.get("/links/goto/stats", headers=auth_headers).json()
    assert stats["total_clicks"] == 1
    assert sum(d["count"] for d in stats["clicks_by_day"]) == 1


def test_redirect_unknown_code_404(client):
    assert client.get("/nope-nope", follow_redirects=False).status_code == 404


def test_stats_requires_ownership(client, auth_headers):
    client.post(
        "/links",
        json={"target_url": "https://example.com", "code": "mine"},
        headers=auth_headers,
    )
    # A different user can't see someone else's stats.
    other = {"email": "eve@example.com", "password": "password123"}
    client.post("/auth/register", json=other)
    token = client.post("/auth/login", json=other).json()["access_token"]
    res = client.get(
        "/links/mine/stats", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 404


def test_delete_link(client, auth_headers):
    client.post(
        "/links",
        json={"target_url": "https://example.com", "code": "tmp"},
        headers=auth_headers,
    )
    assert client.delete("/links/tmp", headers=auth_headers).status_code == 204
    assert client.get("/tmp", follow_redirects=False).status_code == 404
