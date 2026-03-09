from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from models import User, UserRoleEnum


def seed_admin(db: Session):

    admin = db.query(User).filter(User.role == UserRoleEnum.ADMIN).first()

    if admin:
        return

    admin_user = User(
        name="Admin",
        surname1="System",
        surname2="",
        dni="00000000T",
        email="admin@economy.com",
        telephone="+34000000000",
        password=generate_password_hash("Admin123!"),
        role=UserRoleEnum.ADMIN,
        active=True
    )

    db.add(admin_user)