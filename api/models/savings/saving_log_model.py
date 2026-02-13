from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..core.base import Base


class SavingLog(Base):
    __tablename__ = "savings_logs"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    total_amount = Column(Float)
    note = Column(String)

    # Foreign Keys
    saving_id = Column(Integer, ForeignKey('savings.id'), nullable=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)

    # Relationships
    savings = relationship('Saving', back_populates="savings_logs")
    sources = relationship('Source', back_populates='savings_logs')
