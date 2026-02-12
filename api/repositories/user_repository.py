"""Repository for User entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models.models import User


class UserRepository(BaseRepository[User]):
    """Repository for User with custom queries."""

    def __init__(self, db):
        super().__init__(db, User)

    def find_by_dni(self, dni: str):
        """Find user by DNI."""
        return self.db.query(User).filter(User.dni == dni).first()
