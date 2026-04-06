from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..core.base import Base, TimestampMixin


class ImportProfile(TimestampMixin, Base):
    __tablename__ = "import_profiles"

    id = Column(Integer, primary_key=True)

    origin_id = Column(Integer, ForeignKey("import_origins.id"), nullable=False)

    name = Column(String(100), nullable=False)
    header_row_guess = Column(Integer, default=1)
    columns = Column(JSONB, nullable=False)
    active = Column(Boolean, default=True)

    origin = relationship("ImportOrigin", back_populates="profiles")