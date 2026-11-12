"""In-memory revoked-token store keyed by JTI.

Access tokens live 15 minutes and refresh tokens 30 days (jwt_service).
Revoking a JTI blocks it until its original expiry passes, after which the
entry is pruned. Per-process like the login rate limiter: valid while the
app runs a single worker (current deployment).
"""
import threading
import time


class RevokedTokenStore:
    def __init__(self):
        self._revoked: dict[str, float] = {}  # jti -> exp (unix seconds)
        self._lock = threading.Lock()

    def revoke(self, jti: str, exp: float) -> None:
        if not jti or exp <= time.time():
            return
        with self._lock:
            self._revoked[jti] = exp

    def is_revoked(self, jti: str) -> bool:
        with self._lock:
            exp = self._revoked.get(jti)
            if exp is None:
                return False
            if exp <= time.time():
                del self._revoked[jti]
                return False
            return True


revoked_tokens = RevokedTokenStore()
