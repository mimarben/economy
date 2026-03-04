from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import RoleEnum


class HouseholdMember(TimestampMixin, Base):
    __tablename__ = "households_members"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    role = Column(SQLEnum(RoleEnum), nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Foreign Keys
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='households_members')
    household = relationship('Household', back_populates='households_members')
