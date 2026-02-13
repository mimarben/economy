from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from ..core.base import Base


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    type = Column(String, default="income", nullable=False)

    # Relationships
    incomes = relationship('Income', back_populates='sources')
    expenses = relationship('Expense', back_populates='sources')
    savings_logs = relationship("SavingLog", back_populates="sources")
