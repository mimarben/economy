from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import ActionEnum


class InvestmentLog(TimestampMixin, Base):
    __tablename__ = "investments_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    current_value = Column(Numeric(12, 2), nullable=False)
    price_per_unit = Column(Numeric(12, 2))
    units_bought = Column(Numeric(12, 6))
    action = Column(SQLEnum(ActionEnum), nullable=False)
    note = Column(String)

    # Foreign Keys
    investment_id = Column(Integer, ForeignKey('investments.id'), nullable=False, index=True)

    # Relationships
    investment = relationship('Investment', back_populates='investment_logs')
