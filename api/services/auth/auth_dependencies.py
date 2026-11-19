from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from services.auth.jwt_service import decode_token
from services.auth.token_store import revoked_tokens


_bearer_scheme = HTTPBearer(auto_error=False)


def require_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    return _require_token(credentials, "access")


def require_refresh_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    return _require_token(credentials, "refresh")


def get_current_user_id(token: dict = Depends(require_access_token)) -> int:
    """User id from the already-validated access token."""
    return int(token["sub"])


def get_current_user_role(token: dict = Depends(require_access_token)) -> str:
    """Role claim from the already-validated access token ('' if absent)."""
    return token.get("role", "")


def require_role(*roles: str):
    """Dependency factory: allow only tokens whose role claim is in `roles`."""

    def _checker(token: dict = Depends(require_access_token)) -> dict:
        if token.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AUTH_FORBIDDEN",
            )
        return token

    return _checker


def _require_token(
    credentials: HTTPAuthorizationCredentials | None,
    token_type: str,
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AUTH_TOKEN_MISSING",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(credentials.credentials, token_type)
    except InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AUTH_TOKEN_INVALID",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    if revoked_tokens.is_revoked(payload.get("jti", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="AUTH_TOKEN_REVOKED",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
