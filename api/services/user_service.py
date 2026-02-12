"""Service for User implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate, UserRead, UserUpdate
from models.models import User
from services.interfaces import ICRUDService


class UserService(ICRUDService[UserRead, UserCreate, UserUpdate]):
    """Service for User domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    # ICreateService
    def create(self, data: UserCreate) -> UserRead:
        """Create a new user."""
        # Check if user with same DNI exists
        if self.repository.find_by_dni(data.dni):
            raise ValueError("User with this DNI already exists")

        obj = self.repository.create(**data.model_dump())
        return UserRead.model_validate(obj)

    # IReadService
    def get_by_id(self, id: int) -> Optional[UserRead]:
        """Get a single user by ID."""
        obj = self.repository.get_by_id(id)
        if not obj:
            return None
        return UserRead.model_validate(obj)

    def get_all(self) -> List[UserRead]:
        """Get all users."""
        objs = self.repository.get_all()
        return [UserRead.model_validate(obj) for obj in objs]

    # IUpdateService
    def update(self, id: int, data: UserUpdate) -> Optional[UserRead]:
        """Update a user."""
        # Check if DNI changed and if new DNI already exists
        existing = self.repository.get_by_id(id)
        if not existing:
            return None

        if data.dni and data.dni != existing.dni:
            if self.repository.find_by_dni(data.dni):
                raise ValueError("Another user with this DNI already exists")

        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        if not obj:
            return None
        return UserRead.model_validate(obj)

    # IDeleteService
    def delete(self, id: int) -> bool:
        """Delete a user."""
        return self.repository.delete(id)

    # ISearchService
    def search(self, **filters) -> List[UserRead]:
        """Search users by filters."""
        objs = self.repository.search(**filters)
        return [UserRead.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count users matching filters."""
        return self.repository.count(**filters)
