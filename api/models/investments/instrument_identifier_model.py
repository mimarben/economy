import enum

from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Boolean, ForeignKey, func, text, type_coerce
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from ..core.base import Base, TimestampMixin


class IdentifierTypeEnum(str, enum.Enum):
    ISIN = "ISIN"
    TICKER = "TICKER"
    SYMBOL = "SYMBOL"
    PROVIDER = "PROVIDER"
    INTERNAL = "INTERNAL"


class InstrumentIdentifier(TimestampMixin, Base):
    __tablename__ = 'instrument_identifiers'
    # The unique constraint will be created manually in the migration since
    # we cannot reference columns that are defined after the constraint in __table_args__

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id', ondelete='CASCADE'), nullable=False)
    identifier_type = Column(SQLEnum(IdentifierTypeEnum), nullable=False)
    value = Column(String(64), nullable=False)
    exchange = Column(String(16), nullable=True)
    provider = Column(String(32), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)

    # Timestamps (heredados de TimestampMixin)
    # created_at, updated_at, deleted_at

    # Relationships
    instrument = relationship('Instrument', back_populates='identifiers')
