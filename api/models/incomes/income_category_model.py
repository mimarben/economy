from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..core.base import Base


class IncomesCategory(Base):
    __tablename__ = 'incomes_categories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    incomes = relationship('Income', back_populates='categories')
