from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..core.base import Base, TimestampMixin
from ..core.enums import SourceTypeEnum


class Source(TimestampMixin, Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
    type = Column(SQLEnum(SourceTypeEnum), default=SourceTypeEnum.income, nullable=False)

    # Relationships
    incomes = relationship('Income', back_populates='source')
    expenses = relationship('Expense', back_populates='source')
    savings_logs = relationship("SavingLog", back_populates="source")
