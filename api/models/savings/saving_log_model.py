from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin


class SavingLog(TimestampMixin, Base):
    __tablename__ = "savings_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2))
    note = Column(String)

    # Foreign Keys
    saving_id = Column(Integer, ForeignKey('savings.id'), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False, index=True)

    # Relationships
    saving = relationship('Saving', back_populates="savings_logs")
    source = relationship('Source', back_populates='savings_logs')
