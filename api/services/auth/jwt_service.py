from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from config import get_config


_ALGORITHM = "HS256"


def _secret_key() -> str:
    secret = getattr(get_config(), "JWT_SECRET_KEY", None)
    if not secret:
        # Nunca se firma en silencio con el secreto de desarrollo committeado:
        # fuera de desarrollo (APP_ENV=testing/production) la falta de
        # JWT_SECRET_KEY debe ser un error visible, no un fallback.
        raise RuntimeError(
            "JWT_SECRET_KEY no está configurado. Define la variable de entorno "
            "(obligatoria con APP_ENV=production)."
        )
    return secret


def create_access_token(identity: str, additional_claims: dict | None = None) -> str:
    return _create_token(identity, "access", timedelta(minutes=15), additional_claims)


def create_refresh_token(identity: str) -> str:
    return _create_token(identity, "refresh", timedelta(days=30))


def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(token, _secret_key(), algorithms=[_ALGORITHM])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(f"Expected a {expected_type} token")
    return payload


def _create_token(
    identity: str,
    token_type: str,
    expires_in: timedelta,
    additional_claims: dict | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": identity,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "nbf": now,
        "exp": now + expires_in,
    }
    if token_type == "access":
        claims["fresh"] = True
    claims.update(additional_claims or {})
    return jwt.encode(claims, _secret_key(), algorithm=_ALGORITHM)
