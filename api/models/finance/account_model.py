from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import CurrencyEnum

class Account(TimestampMixin, Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        UniqueConstraint('iban', name='uq_accounts_iban'),
    )
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    iban = Column(String, nullable=False, unique=True)
    currency = Column(SQLEnum(CurrencyEnum), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    balance = Column(Numeric(12, 2), nullable=True)
    
    # Foreign Keys
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False, index=True)
    import_origin_id = Column(Integer, ForeignKey("import_origins.id"))
    import_profile_id = Column(Integer,ForeignKey("import_profiles.id"),nullable=True)
    
    # Relationships
    users = relationship('User', back_populates='accounts', secondary='account_users', overlaps='account_users')
    account_users = relationship('AccountUser', back_populates='account', cascade='all, delete-orphan', overlaps='users')
    bank = relationship('Bank', back_populates='accounts')    
    savings = relationship('Saving', back_populates='account')
    investments = relationship('Investment', back_populates='account')
    expenses = relationship('Expense', back_populates='account')
    incomes = relationship('Income', back_populates='account')
    cards = relationship('Card', back_populates='account')
    import_origin = relationship("ImportOrigin", back_populates="accounts")
    import_profile = relationship("ImportProfile")