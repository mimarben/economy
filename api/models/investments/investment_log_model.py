from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base
from ..core.enums import ActionEnum


class InvestmentLog(Base):
    __tablename__ = "investments_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    currentValue = Column(Float, nullable=False)
    pricePerUnit = Column(Float)
    unitsBought = Column(Float)
    action = Column(SQLEnum(ActionEnum), nullable=False)
    note = Column(String)

    # Foreign Keys
    investment_id = Column(Integer, ForeignKey('investments.id'), nullable=False)

    # Relationships
    investments = relationship('Investment', back_populates='investment_logs')
