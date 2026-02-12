"""Service for User implementing CRUD operations."""
from typing import Optional
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate, UserRead, UserUpdate
from models.models import User
from services.base_service import BaseService


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

        return super().create(data)

    def update(self, id: int, data: UserUpdate) -> Optional[UserRead]:
        """Update a user with DNI change validation."""
        # Check if DNI changed and if new DNI already exists
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        if data.dni and data.dni != existing.dni:
            if self.repository.find_by_dni(data.dni):
                raise ValueError("Another user with this DNI already exists")

        return super().update(id, data)
