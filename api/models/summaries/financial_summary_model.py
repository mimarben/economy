from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class FinancialSummary(TimestampMixin, Base):
    __tablename__ = "financials_summaries"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    total_income = Column(Numeric(12, 2), nullable=False)
    total_expenses = Column(Numeric(12, 2), nullable=False)
    total_savings = Column(Numeric(12, 2), nullable=False)
    total_investments = Column(Numeric(12, 2), nullable=False)
    net_worth = Column(Numeric(12, 2), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    household_id = Column(Integer, ForeignKey('households.id'), nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='financials_summaries')
