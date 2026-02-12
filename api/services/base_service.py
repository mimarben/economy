from typing import Type, Generic, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session
from services.interfaces import ICRUDService

ModelT = TypeVar("ModelT")
ReadT = TypeVar("ReadT")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")


class BaseService(
    ICRUDService[ReadT, CreateT, UpdateT],
    Generic[ModelT, ReadT, CreateT, UpdateT]
):
    """
    Generic CRUD service implementation.

    Handles the common logic for all services:
    - Converting between ORM models and Pydantic schemas
    - Delegating database operations to repositories
    - Maintaining separation between domain and presentation layers
    """

    def __init__(
        self,
        db: Session,
        model: Type[ModelT],
        repository: Any,
        read_schema: Type[ReadT]
    ):
        self.db = db
        self.model = model
        self.repository = repository
        self.read_schema = read_schema

    def create(self, data: CreateT) -> ReadT:
        obj = self.model(**data.model_dump())
        obj = self.repository.create(obj)
        return self.read_schema.model_validate(obj)

    def get_by_id(self, id: int) -> Optional[ReadT]:
        obj = self.repository.get_by_id(id)
        return self.read_schema.model_validate(obj) if obj else None

    def get_all(self) -> List[ReadT]:
        objs = self.repository.get_all()
        return [self.read_schema.model_validate(o) for o in objs]

    def update(self, id: int, data: UpdateT) -> Optional[ReadT]:
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        return self.read_schema.model_validate(obj) if obj else None

    def delete(self, id: int) -> bool:
        return self.repository.delete(id)

    def search(self, **filters) -> List[ReadT]:
        objs = self.repository.search(**filters)
        return [self.read_schema.model_validate(o) for o in objs]

    def count(self, **filters) -> int:
        return self.repository.count(**filters)
