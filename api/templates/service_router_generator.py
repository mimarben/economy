"""
Template generator for CRUD services and routers following ISP.

This script helps create consistent service and router implementations.
"""

SERVICE_TEMPLATE = '''"""Service for {entity_name} implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.{entity_file}_repository import {entity_class}Repository
from schemas.{entity_file}_schema import {entity_class}Create, {entity_class}Read, {entity_class}Update
from models import {entity_class}
from services.interfaces import ICRUDService


class {entity_class}Service(ICRUDService[{entity_class}Read, {entity_class}Create, {entity_class}Update]):
    """Service for {entity_name} domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = {entity_class}Repository(db)

    # ICreateService methods
    def create(self, data: {entity_class}Create) -> {entity_class}Read:
        """Create a new {entity_name}."""
        obj = {entity_class}(**data.model_dump())
        obj = self.repository.create(obj)
        self.db.commit()
        return {entity_class}Read.model_validate(obj)

    # IReadService methods
    def get_by_id(self, id: int) -> Optional[{entity_class}Read]:
        """Get a single {entity_name} by ID."""
        obj = self.repository.get_by_id(id)
        if not obj:
            return None
        return {entity_class}Read.model_validate(obj)

    def get_all(self) -> List[{entity_class}Read]:
        """Get all {entity_name}s."""
        objs = self.repository.get_all()
        return [{entity_class}Read.model_validate(obj) for obj in objs]

    # IUpdateService methods
    def update(self, id: int, data: {entity_class}Update) -> Optional[{entity_class}Read]:
        """Update a {entity_name}."""
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        if not obj:
            return None
        self.db.commit()
        return {entity_class}Read.model_validate(obj)

    # IDeleteService methods
    def delete(self, id: int) -> bool:
        """Delete a {entity_name}."""
        success = self.repository.delete(id)
        if success:
            self.db.commit()
        return success

    # ISearchService methods
    def search(self, **filters) -> List[{entity_class}Read]:
        """Search {entity_name}s by filters."""
        objs = self.repository.search(**filters)
        return [{entity_class}Read.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count {entity_name}s matching filters."""
        return self.repository.count(**filters)
'''

ROUTER_TEMPLATE = '''"""Router for {entity_name} endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from utils.i18n import _

from schemas.{entity_file}_schema import {entity_class}Create, {entity_class}Update
from services.{entity_file}_service import {entity_class}Service
from db.database import get_db
from services.core.response_service import Response


router = APIRouter()
name = "{entity_plural}"


def _get_service(db: Session) -> {entity_class}Service:
    """Dependency: service bound to the request session."""
    return {entity_class}Service(db)


@router.post("/{entity_plural}")
def create_{entity_name}(payload: {entity_class}Create, db: Session = Depends(get_db)):
    """Create a new {entity_name}."""
    service = _get_service(db)
    try:
        result = service.create(payload)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)
    return Response.ok_data(result.model_dump(), _("{entity_upper}_CREATED"), 201, name)


@router.get("/{entity_plural}/{{{entity_name}_id:int}}")
def get_{entity_name}({entity_name}_id: int, db: Session = Depends(get_db)):
    """Get a single {entity_name} by ID."""
    service = _get_service(db)
    result = service.get_by_id({entity_name}_id)

    if not result:
        return Response.error(_("{entity_upper}_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_data(result.model_dump(), _("{entity_upper}_FOUND"), 200, name)


@router.get("/{entity_plural}")
def list_{entity_plural}(db: Session = Depends(get_db)):
    """Get all {entity_name}s."""
    service = _get_service(db)
    results = service.get_all()

    return Response.ok_data(
        [r.model_dump() for r in results],
        _("{entity_upper}_LIST"),
        200,
        name
    )


@router.patch("/{entity_plural}/{{{entity_name}_id:int}}")
def update_{entity_name}({entity_name}_id: int, payload: {entity_class}Update, db: Session = Depends(get_db)):
    """Update a {entity_name}."""
    service = _get_service(db)
    try:
        result = service.update({entity_name}_id, payload)
    except ValueError as e:
        return Response.error(_("INVALID_DATA"), str(e), 400, name)

    if not result:
        return Response.error(_("{entity_upper}_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_data(result.model_dump(), _("{entity_upper}_UPDATED"), 200, name)


@router.delete("/{entity_plural}/{{{entity_name}_id:int}}")
def delete_{entity_name}({entity_name}_id: int, db: Session = Depends(get_db)):
    """Delete a {entity_name}."""
    service = _get_service(db)
    success = service.delete({entity_name}_id)

    if not success:
        return Response.error(_("{entity_upper}_NOT_FOUND"), _("NONE"), 404, name)

    return Response.ok_message(_("{entity_upper}_DELETED"), 204, name)
'''


REPOSITORY_TEMPLATE = '''"""Repository for {entity_name} entity."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models import {entity_class}


class {entity_class}Repository(BaseRepository[{entity_class}]):
    """Repository for {entity_class} with custom queries."""

    def __init__(self, db: Session):
        super().__init__(db, {entity_class})

    # Add custom domain-specific queries here
    # Example:
    # def get_by_custom_field(self, value) -> List[{entity_class}]:
    #     stmt = select({entity_class}).where({entity_class}.custom_field == value)
    #     return self.db.execute(stmt).scalars().all()
'''

if __name__ == "__main__":
    # Example usage
    entities = [
        {"class": "User", "name": "user", "plural": "users", "file": "user"},
        {"class": "Bank", "name": "bank", "plural": "banks", "file": "bank"},
        # Add more...
    ]

    for entity in entities:
        # Generate service code
        service_code = SERVICE_TEMPLATE.format(
            entity_class=entity["class"],
            entity_name=entity["name"],
            entity_file=entity["file"],
        )
        print(f"# Service for {entity['class']}")
        print(service_code)
        print("\n" + "="*80 + "\n")
