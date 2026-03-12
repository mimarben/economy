from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class InvestmentsCategory(TimestampMixin, Base):
    __tablename__ = 'investments_categories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    investments = relationship('Investment', back_populates='category')
