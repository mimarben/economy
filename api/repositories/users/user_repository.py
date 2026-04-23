"""Repository for User entity following segregated interfaces."""
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from repositories.core.base_repository import BaseRepository
from models import User


class UserRepository(BaseRepository[User]):
    """Repository for User with custom queries."""

    def __init__(self, db):
        super().__init__(db, User)

    def get_all(self, page: int = 1, per_page: int = 50):
        stmt = self._base_query().options(selectinload(User.accounts)).offset((page - 1) * per_page).limit(per_page)
        return self.db.execute(stmt).scalars().all()

    def find_by_dni(self, dni: str):
        """Find user by DNI."""
        stmt = self._base_query().where(User.dni == dni)
        return self.db.execute(stmt).scalar_one_or_none()
    def find_by_email(self, email: str):
        """Find user by email."""
        stmt = self._base_query().where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
