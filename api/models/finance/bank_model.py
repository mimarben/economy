from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class Bank(TimestampMixin, Base):
    __tablename__ = 'banks'
    __table_args__ = (
        UniqueConstraint('cif', name='uq_banks_cif'),
    )
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    cif = Column(String, nullable=True)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)

    # Relationships
    accounts = relationship('Account', back_populates='bank')
