from sqlalchemy.orm import Session
from models.models import User

class UserService:
    @staticmethod
    def user_exists(db: Session, dni: str, exclude_user_id: int = None) -> bool:
        """Check if another user already has the given DNI, excluding a specific user if needed."""
        query = db.query(User).filter(User.dni == dni)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None
