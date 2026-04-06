from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..core.base import Base, TimestampMixin


class ImportOrigin(TimestampMixin, Base):
    __tablename__ = "import_origins"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # ING, AMEX
    name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
     
     # Relationships
    accounts = relationship("Account", back_populates="import_origin")
    cards = relationship("Card", back_populates="import_origin")
    profiles = relationship("ImportProfile", back_populates="origin", lazy="selectin")