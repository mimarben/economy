from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import UserRoleEnum


class User(TimestampMixin, Base):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('dni', name='uq_users_dni'),
    )
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    surname1 = Column(String, nullable=False)
    surname2 = Column(String)
    dni = Column(String, nullable=False)
    email = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    telephone = Column(Integer)
    password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.USER, nullable=False)

    # Relationships
    accounts = relationship('Account', back_populates='user')
    households_members = relationship('HouseholdMember', back_populates='user')
