from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base


class FinancialSummary(Base):
    __tablename__ = "financials_summaries"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    total_income = Column(Float, nullable=False)
    total_expenses = Column(Float, nullable=False)
    total_savings = Column(Float, nullable=False)
    total_investments = Column(Float, nullable=False)
    net_worth = Column(Float, nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='financials_summaries')
