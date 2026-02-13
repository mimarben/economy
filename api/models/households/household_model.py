from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..core.base import Base


class Household(Base):
    __tablename__ = "households"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    households_members = relationship('HouseholdMember', back_populates='households')
