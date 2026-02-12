"""
Template generator for CRUD services and routers following ISP.

This script helps create consistent service and router implementations.
"""

SERVICE_TEMPLATE = '''"""Service for {entity_name} implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.{entity_file}_repository import {entity_class}Repository
from schemas.{entity_file}_schema import {entity_class}Create, {entity_class}Read, {entity_class}Update
from models.models import {entity_class}
from services.interfaces import ICRUDService


class {entity_class}Service(ICRUDService[{entity_class}Read, {entity_class}Create, {entity_class}Update]):
    """Service for {entity_name} domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = {entity_class}Repository(db)

    # ICreateService methods
    def create(self, data: {entity_class}Create) -> {entity_class}Read:
        """Create a new {entity_name}."""
        obj = self.repository.create(**data.model_dump())
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
        return {entity_class}Read.model_validate(obj)

    # IDeleteService methods
    def delete(self, id: int) -> bool:
        """Delete a {entity_name}."""
        return self.repository.delete(id)

    # ISearchService methods
    def search(self, **filters) -> List[{entity_class}Read]:
        """Search {entity_name}s by filters."""
        objs = self.repository.search(**filters)
        return [{entity_class}Read.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count {entity_name}s matching filters."""
        return self.repository.count(**filters)
'''

ROUTER_TEMPLATE = '''"""Router for {entity_name} endpoints following ISP."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.{entity_file}_schema import {entity_class}Create, {entity_class}Update
from services.{entity_file}_service import {entity_class}Service
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService, ISearchService
from db.database import get_db
from services.response_service import Response


router = Blueprint('{entity_plural}', __name__)
name = "{entity_plural}"


def _get_create_service(db: Session) -> ICreateService:
    """Dependency: Inject only create service."""
    return {entity_class}Service(db)


def _get_read_service(db: Session) -> IReadService:
    """Dependency: Inject only read service."""
    return {entity_class}Service(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Dependency: Inject only update service."""
    return {entity_class}Service(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Dependency: Inject only delete service."""
    return {entity_class}Service(db)


def _get_search_service(db: Session) -> ISearchService:
    """Dependency: Inject only search service."""
    return {entity_class}Service(db)


@router.post("/{entity_plural}")
def create_{entity_name}():
    """Create a new {entity_name}."""
    db: Session = next(get_db())

    try:
        data = {entity_class}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("{entity_upper}_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{entity_plural}/<int:{entity_name}_id>")
def get_{entity_name}({entity_name}_id):
    """Get a single {entity_name} by ID."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id({entity_name}_id)

        if not result:
            return Response._error(_("{entity_upper}_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("{entity_upper}_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{entity_plural}")
def list_{entity_plural}():
    """Get all {entity_name}s."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()

        return Response._ok_data(
            [r.model_dump() for r in results],
            _("{entity_upper}_LIST"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/{entity_plural}/<int:{entity_name}_id>")
def update_{entity_name}({entity_name}_id):
    """Update a {entity_name}."""
    db: Session = next(get_db())

    try:
        data = {entity_class}Update.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update({entity_name}_id, data)

        if not result:
            return Response._error(_("{entity_upper}_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("{entity_upper}_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/{entity_plural}/<int:{entity_name}_id>")
def delete_{entity_name}({entity_name}_id):
    """Delete a {entity_name}."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete({entity_name}_id)

        if not success:
            return Response._error(_("{entity_upper}_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_message(_("{entity_upper}_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
'''


REPOSITORY_TEMPLATE = '''"""Repository for {entity_name} entity."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.models import {entity_class}


class {entity_class}Repository(BaseRepository[{entity_class}]):
    """Repository for {entity_class} with custom queries."""

    def __init__(self, db: Session):
        super().__init__(db, {entity_class})

    # Add custom domain-specific queries here
    # Example:
    # def get_by_custom_field(self, value) -> List[{entity_class}]:
    #     return self.db.query({entity_class}).filter({entity_class}.custom_field == value).all()
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
