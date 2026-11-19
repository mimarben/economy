"""Service for User implementing CRUD operations."""
import secrets
import string
from typing import Optional
from sqlalchemy.orm import Session
from repositories.users.user_repository import UserRepository
from schemas.users.user_schema import UserCreate, UserRead, UserUpdate
from models import User, UserRoleEnum
from services.core.base_service import BaseService
from services.core.security_service import hash_password

# Alphabet for generated passwords: every class required by check_password().
_PWD_LOWER = string.ascii_lowercase
_PWD_UPPER = string.ascii_uppercase
_PWD_DIGITS = string.digits
_PWD_SYMBOLS = "!$%*?&-_"
_PWD_LENGTH = 12


class UserService(BaseService[User, UserRead, UserCreate, UserUpdate]):
    """Service for User domain logic with custom DNI validation."""

    def __init__(self, db: Session):
        super().__init__(
            db=db,
            model=User,
            repository=UserRepository(db),
            read_schema=UserRead
        )

    def create(self, data: UserCreate) -> UserRead:
        """Create a new user with DNI uniqueness validation."""
        # Check if user with same DNI exists
        if self.repository.find_by_dni(data.dni):
            raise ValueError("User with this DNI already exists")
        # Hash password
        data.password = hash_password(data.password)
        return super().create(data)

    def update(
        self,
        id: int,
        data: UserUpdate,
        *,
        current_user_id: Optional[int] = None,
        current_role: Optional[str] = None,
    ) -> Optional[UserRead]:
        """Update a user with DNI change validation and role guards.

        `current_user_id`/`current_role` come from the access token. When they
        are omitted (e.g. internal calls) no role guard is applied, keeping the
        previous behaviour intact.
        """
        # Check if DNI changed and if new DNI already exists
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        is_admin = current_role == UserRoleEnum.ADMIN.value
        is_self = current_user_id == id
        role_changes = data.role is not None and data.role != existing.role

        # Role guards apply only when caller context (from the access token)
        # is supplied; internal calls keep the previous behaviour.
        if current_role is not None:
            # A non-admin can never change roles (no privilege escalation).
            if not is_admin and role_changes:
                raise ValueError("ROLE_CHANGE_FORBIDDEN")

            # An admin cannot change their own role (avoids self-lockout and
            # silently dropping the last administrator).
            if is_self and role_changes:
                raise ValueError("OWN_ROLE_CHANGE_FORBIDDEN")

        # Never demote or deactivate the last active administrator.
        demotes_admin = existing.role == UserRoleEnum.ADMIN and role_changes
        deactivates_admin = existing.role == UserRoleEnum.ADMIN and data.active is False
        if (demotes_admin or deactivates_admin) and self.repository.count_active_admins() <= 1:
            raise ValueError("LAST_ADMIN_PROTECTED")

        if data.dni and data.dni != existing.dni:
            if self.repository.find_by_dni(data.dni):
                raise ValueError("Another user with this DNI already exists")
        if data.password:
            data.password = hash_password(data.password)
        return super().update(id, data)

    def reset_password(self, id: int) -> Optional[dict]:
        """Generate a new random password for a user (admin action).

        Returns the updated user together with the plaintext password exactly
        once; only its hash is persisted.
        """
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        alphabet = _PWD_LOWER + _PWD_UPPER + _PWD_DIGITS + _PWD_SYMBOLS
        # One character of every policy class, then random fill, then a
        # secrets-based Fisher-Yates shuffle.
        chars = [
            secrets.choice(_PWD_LOWER),
            secrets.choice(_PWD_UPPER),
            secrets.choice(_PWD_DIGITS),
            secrets.choice(_PWD_SYMBOLS),
        ] + [secrets.choice(alphabet) for _ in range(_PWD_LENGTH - 4)]
        for i in range(len(chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            chars[i], chars[j] = chars[j], chars[i]
        temporary_password = "".join(chars)

        updated = self.repository.update(id, password=hash_password(temporary_password))
        self.db.commit()
        return {
            "user": self.read_schema.model_validate(updated),
            "temporary_password": temporary_password,
        }
