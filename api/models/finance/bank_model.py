from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..core.base import Base


class Bank(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    accounts = relationship('Account', back_populates='banks')
