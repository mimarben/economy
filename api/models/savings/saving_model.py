from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base
from ..core.enums import CurrencyEnum


class Saving(Base):
    __tablename__ = 'savings'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    description = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)

    # Relationships
    users = relationship('User', back_populates='savings')
    accounts = relationship('Account', back_populates='savings')
    savings_logs = relationship("SavingLog", back_populates="savings")
