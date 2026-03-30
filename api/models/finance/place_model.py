from sqlalchemy import Column, Integer, String, Boolean

from ..core.base import Base, TimestampMixin


class Place(TimestampMixin, Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String)
    description = Column(String)
    active = Column(Boolean, default=True, nullable=False)
