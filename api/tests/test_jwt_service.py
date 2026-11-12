"""JWT service tests: legacy Flask token compatibility + secret selection.

Dos regresiones de la migración Flask → FastAPI:

1. La API anterior firmaba con flask-jwt-extended 4.7.1, que construye los
   claims en ``tokens.py::_encode_jwt``: ``fresh``, ``iat``, ``jti``,
   ``type`` ("access"|"refresh"), ``sub``, ``nbf`` y ``exp``. El antiguo
   ``AuthService.login`` añadía ``role``/``email`` como additional_claims del
   access token. La implementación PyJWT actual usa los mismos nombres de
   claims, por lo que los tokens emitidos antes de la migración (con el mismo
   JWT_SECRET_KEY) deben seguir descodificándose sin cambios.
2. ``_secret_key()`` no debe caer en silencio al secreto de desarrollo
   committeado cuando no hay JWT_SECRET_KEY fuera de desarrollo.
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from config import DevelopmentConfig
from services.auth import jwt_service


# ─────────────── tokens legacy (flask-jwt-extended 4.7.1) ───────────────


def _legacy_flask_jwt_extended_token(token_type: str) -> str:
    """Token con la forma exacta que producía flask-jwt-extended 4.7.1."""
    now = datetime.now(timezone.utc)
    claims = {
        "fresh": token_type == "access",
        "iat": now,
        "jti": str(uuid4()),
        "type": token_type,
        "sub": "1",
        "nbf": now,
        "exp": now + timedelta(days=30),
    }
    if token_type == "access":
        # additional_claims del antiguo AuthService.login
        claims["role"] = "user"
        claims["email"] = "login@example.com"
    return jwt.encode(claims, jwt_service._secret_key(), algorithm="HS256")


def test_legacy_refresh_token_is_accepted():
    token = _legacy_flask_jwt_extended_token("refresh")

    payload = jwt_service.decode_token(token, "refresh")

    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"


def test_legacy_access_token_is_accepted():
    token = _legacy_flask_jwt_extended_token("access")

    payload = jwt_service.decode_token(token, "access")

    assert payload["sub"] == "1"
    assert payload["role"] == "user"
    assert payload["email"] == "login@example.com"


def test_legacy_refresh_token_cannot_be_used_as_access():
    token = _legacy_flask_jwt_extended_token("refresh")

    with pytest.raises(jwt.InvalidTokenError):
        jwt_service.decode_token(token, "access")


# ─────────────── selección de secreto (APP_ENV) ───────────────


def test_secret_key_uses_dev_fallback_in_development(monkeypatch):
    monkeypatch.setattr("config.Config.JWT_SECRET_KEY", None)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    assert jwt_service._secret_key() == DevelopmentConfig.JWT_SECRET_KEY


def test_secret_key_refuses_dev_fallback_in_production(monkeypatch):
    monkeypatch.setattr("config.Config.JWT_SECRET_KEY", None)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        jwt_service._secret_key()


def test_secret_key_uses_testing_secret_when_app_env_testing(monkeypatch):
    monkeypatch.setattr("config.Config.JWT_SECRET_KEY", None)
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    assert jwt_service._secret_key() == "testing-jwt-secret"
