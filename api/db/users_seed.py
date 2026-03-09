from sqlalchemy.orm import Session
from services.core.security_service import hash_password

from models import User, UserRoleEnum
import os
from dotenv import load_dotenv

load_dotenv()

def seed_admin(db: Session):

    admin = db.query(User).filter(User.role == UserRoleEnum.ADMIN).first()

    if admin:
        return

    admin_user = User(
        name="Admin",
        surname1="System",
        surname2="",
        dni="00000000T",
        email=os.getenv("POSTGRES_ADMIN_EMAIL"),
        telephone="676767676",
        password=hash_password(os.getenv("POSTGRES_ADMIN_PASSWORD")),
        role=UserRoleEnum.ADMIN,
        active=True
    )

    db.add(admin_user)