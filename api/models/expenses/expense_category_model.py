from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..core.base import Base


class ExpensesCategory(Base):
    __tablename__ = 'expenses_categories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    expenses = relationship('Expense', back_populates='categories')
