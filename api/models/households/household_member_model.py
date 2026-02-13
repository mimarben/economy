from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base
from ..core.enums import RoleEnum


class HouseholdMember(Base):
    __tablename__ = "households_members"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Foreign Keys
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='households_members')
    households = relationship('Household', back_populates='households_members')
