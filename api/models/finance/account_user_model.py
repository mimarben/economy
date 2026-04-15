from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class AccountUser(TimestampMixin, Base):
    __tablename__ = 'account_users'
    __table_args__ = (
        UniqueConstraint('account_id', 'user_id', name='uq_account_user'),
    )
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Relationships
    account = relationship('Account', back_populates='account_users')
    user = relationship('User', back_populates='account_users')
