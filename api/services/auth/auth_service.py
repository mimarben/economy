"""Authentication service handling login, register, and token operations."""
from typing import Optional
from sqlalchemy.orm import Session
from flask_jwt_extended import create_access_token, create_refresh_token

from services.core.security_service import hash_password, verify_password
from models import User, UserRoleEnum
from repositories.users.user_repository import UserRepository
from schemas.auth.auth_schema import LoginRequest, TokenResponse, RefreshResponse
from schemas.users.user_schema import UserRead

# Setup logging
from services.logs.logger_service import setup_logger
logger = setup_logger("auth")


class AuthService:
    """Handles authentication business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)
    def login(self, data: LoginRequest) -> Optional[TokenResponse]:
        """Authenticate user and return JWT tokens."""
        user = self.repository.find_by_email(data.email)

        if not user:
            logger.warning(f"Login attempt with unknown email: {data.email}")
            return None

        if not user.active:
            logger.warning(f"Login attempt for deactivated user: {data.email}")
            return None

        if not verify_password(data.password, user.password):
            logger.warning(f"Invalid password for user: {data.email}")
            return None

        # Create tokens with user identity
        identity = str(user.id)
        access_token = create_access_token(
            identity=identity,
            additional_claims={"role": user.role.value, "email": user.email}
        )
        refresh_token = create_refresh_token(identity=identity)

        logger.info(f"User logged in successfully: {data.email}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def refresh(self, user_id: str) -> RefreshResponse:
        """Generate a new access token from refresh token identity."""
        user = self.repository.get_by_id(int(user_id))
        if not user:
            raise ValueError("USER_NOT_FOUND")

        access_token = create_access_token(
            identity=user_id,
            additional_claims={"role": user.role.value, "email": user.email}
        )

        return RefreshResponse(access_token=access_token)

    def get_current_user(self, user_id: str) -> Optional[UserRead]:
        """Get user data by ID (from JWT identity)."""
        user = self.repository.get_by_id(int(user_id))
        if not user:
            return None
        return UserRead.model_validate(user)
