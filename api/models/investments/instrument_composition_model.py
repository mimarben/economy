from sqlalchemy import Column, Integer, Numeric, Date, String, ForeignKey, DateTime, text as sa_text, func, UniqueConstraint as sa_UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from ..core.base import Base, TimestampMixin


class InstrumentComposition(TimestampMixin, Base):
    __tablename__ = 'instrument_compositions'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    parent_instrument_id = Column(Integer, ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    child_instrument_id = Column(Integer, ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Numeric(18, 10), nullable=False)
    weight = Column(Numeric(18, 10), nullable=True)
    source = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        sa_UniqueConstraint('parent_instrument_id', 'child_instrument_id', name='uq_instrument_composition_unique'),
    )

    # Relationships
    parent_instrument = relationship('Instrument', foreign_keys=[parent_instrument_id], back_populates='compositions_parent')
    child_instrument = relationship('Instrument', foreign_keys=[child_instrument_id], back_populates='compositions_child')
