from datetime import datetime
from typing import TypeVar, Type, List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from repositories.core.interfaces import ICRUDRepository

T = TypeVar('T')


class BaseRepository(ICRUDRepository[T]):

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    # ======================
    # BASE QUERY
    # ======================

    def _base_query(self):
        stmt = select(self.model)
        if hasattr(self.model, 'deleted_at'):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return stmt

    # ======================
    # READ
    # ======================

    def get_by_id(self, id: int) -> Optional[T]:
        stmt = self._base_query().where(self.model.id == id)
        return self.db.execute(stmt).scalars().one_or_none()

    def get_all(self, page: int = 1, per_page: int = 50) -> List[T]:
        stmt = self._base_query().offset((page - 1) * per_page).limit(per_page)
        return self.db.execute(stmt).scalars().all()

    def get_all_unpaginated(self) -> List[T]:
        stmt = self._base_query()
        return self.db.execute(stmt).scalars().all()

    # ======================
    # WRITE
    # ======================

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, **kwargs) -> Optional[T]:
        obj = self.get_by_id(id)
        if not obj:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False

        if hasattr(obj, 'deleted_at'):
            obj.deleted_at = datetime.utcnow()
        else:
            self.db.delete(obj)

        self.db.commit()
        return True

    def hard_delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True

    # ======================
    # SEARCH
    # ======================

    def search(self, **filters) -> List[T]:
        stmt = self._base_query()

        for key, value in filters.items():
            if "__" in key:
                field, op = key.split("__", 1)
            else:
                field, op = key, "eq"

            if not hasattr(self.model, field):
                continue

            column = getattr(self.model, field)

            if op == "eq":
                stmt = stmt.where(column == value)
            elif op == "gte":
                stmt = stmt.where(column >= value)
            elif op == "lte":
                stmt = stmt.where(column <= value)
            elif op == "like":
                stmt = stmt.where(column.ilike(f"%{value}%"))
            elif op == "in":
                if isinstance(value, list):
                    stmt = stmt.where(column.in_(value))

        return self.db.execute(stmt).scalars().all()

    # ======================
    # COUNT
    # ======================

    def count(self, **filters) -> int:
        base = self._base_query().subquery()
        stmt = select(func.count()).select_from(base)

        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)

        return self.db.execute(stmt).scalar_one()