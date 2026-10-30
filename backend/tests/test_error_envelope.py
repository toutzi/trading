def test_unknown_route_returns_not_found_envelope(client):
    r = client.get("/does-not-exist")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_validation_error_uses_locked_envelope_shape(client):
    r = client.post("/auth/login", json={})
    assert r.status_code == 422
    body = r.json()
    assert set(body.keys()) == {"error"}
    assert set(body["error"].keys()) == {"code", "message"}
    assert body["error"]["code"] == "validation_error"


def test_every_non_2xx_uses_envelope(client):
    # spot-check the three non-2xx classes: 401, 404, 422
    r401 = client.get("/me")
    r404 = client.get("/nope")
    r422 = client.post("/auth/login", json={})
    for r in (r401, r404, r422):
        assert r.status_code >= 400
        assert "error" in r.json()
        assert "code" in r.json()["error"]
        assert "message" in r.json()["error"]
