from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..core.base import Base, TimestampMixin


class ImportProfile(TimestampMixin, Base):
    __tablename__ = "import_profiles"
    __table_args__ = (
        UniqueConstraint("origin_id", "name", name="uq_origin_profile_name"),
    )
    id = Column(Integer, primary_key=True)

    origin_id = Column(
        Integer,
        ForeignKey("import_origins.id"),
        nullable=False,
        index=True
    )
    file_type = Column(String(20), nullable=True)
    name = Column(String(100), nullable=False)
    header_row_guess = Column(Integer, default=1)
    columns = Column(JSONB, nullable=False)
    active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    origin = relationship("ImportOrigin", back_populates="profiles")