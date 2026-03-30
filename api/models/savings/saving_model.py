from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum


class Saving(TimestampMixin, Base):
    __tablename__ = 'savings'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)

    # Foreign Keys
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)

    # Relationships
    account = relationship('Account', back_populates='savings')
    savings_logs = relationship("SavingLog", back_populates="saving")
