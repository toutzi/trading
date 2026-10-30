def test_openapi_declares_login_and_me(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "/auth/login" in spec["paths"]
    assert "/me" in spec["paths"]


def test_openapi_bearer_auth_scheme_matches_contract(client):
    r = client.get("/openapi.json")
    spec = r.json()
    schemes = spec.get("components", {}).get("securitySchemes", {})
    assert "bearerAuth" in schemes
    scheme = schemes["bearerAuth"]
    assert scheme["type"] == "http"
    assert scheme["scheme"] == "bearer"
    assert scheme["bearerFormat"] == "JWT"


def test_top_level_security_defaults_to_bearer_auth(client):
    r = client.get("/openapi.json")
    spec = r.json()
    assert spec["security"] == [{"bearerAuth": []}]


def test_login_is_public_with_explicit_empty_security(client):
    r = client.get("/openapi.json")
    spec = r.json()
    login_op = spec["paths"]["/auth/login"]["post"]
    assert login_op["security"] == []


def test_me_inherits_global_security(client):
    r = client.get("/openapi.json")
    spec = r.json()
    me_op = spec["paths"]["/me"]["get"]
    assert "security" not in me_op


def test_validation_error_schema_is_error_envelope_not_http_validation(client):
    # Guards against the default 422 `detail` array leaking into the contract.
    r = client.get("/openapi.json")
    spec = r.json()
    login_422 = spec["paths"]["/auth/login"]["post"]["responses"]["422"]
    schema = login_422["content"]["application/json"]["schema"]
    assert schema == {"$ref": "#/components/schemas/ErrorEnvelope"}
    assert "HTTPValidationError" not in spec["components"]["schemas"]
    assert "ValidationError" not in spec["components"]["schemas"]


def test_error_code_enum_emitted_with_contract_values(client):
    r = client.get("/openapi.json")
    spec = r.json()
    code_schema = spec["components"]["schemas"]["ErrorCode"]
    assert code_schema["type"] == "string"
    assert set(code_schema["enum"]) == {
        "invalid_credentials",
        "unauthorized",
        "invalid_token",
        "validation_error",
        "not_found",
        "internal_error",
    }


def test_error_detail_code_is_enum_reference_not_bare_string(client):
    r = client.get("/openapi.json")
    spec = r.json()
    code_field = spec["components"]["schemas"]["ErrorDetail"]["properties"]["code"]
    assert code_field == {"$ref": "#/components/schemas/ErrorCode"}
