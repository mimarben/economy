#!/usr/bin/env python3
"""Auto-generate CRUD services and routers following ISP pattern."""

from pathlib import Path

# Map of entities to generate
ENTITIES = [
    {"class": "User", "singular": "user", "plural": "users"},
    {"class": "Bank", "singular": "bank", "plural": "banks"},
    {"class": "Account", "singular": "account", "plural": "accounts"},
    {"class": "Source", "singular": "source", "plural": "sources"},
    {"class": "ExpensesCategory", "singular": "expense_category", "plural": "expense_categories"},
    {"class": "IncomesCategory", "singular": "income_category", "plural": "income_categories"},
    {"class": "Income", "singular": "income", "plural": "incomes"},
    {"class": "Saving", "singular": "saving", "plural": "savings"},
    {"class": "SavingLog", "singular": "saving_log", "plural": "saving_logs"},
    {"class": "InvestmentsCategory", "singular": "investment_category", "plural": "investment_categories"},
    {"class": "Investment", "singular": "investment", "plural": "investments"},
    {"class": "InvestmentLog", "singular": "investment_log", "plural": "investment_logs"},
    {"class": "FinancialSummary", "singular": "financial_summary", "plural": "financial_summaries"},
    {"class": "Household", "singular": "household", "plural": "households"},
    {"class": "HouseholdMember", "singular": "household_member", "plural": "household_members"},
]

REPOSITORY_TEMPLATE = '''"""Repository for {class_name} entity following segregated interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from models.models import {class_name}


class {class_name}Repository(BaseRepository[{class_name}]):
    """Repository for {class_name} with custom queries."""

    def __init__(self, db: Session):
        super().__init__(db, {class_name})

    # Add custom domain-specific queries here
    # Example:
    # def get_by_custom_field(self, value) -> List[{class_name}]:
    #     return self.db.query({class_name}).filter({class_name}.custom_field == value).all()
'''

SERVICE_TEMPLATE = '''"""Service for {class_name} implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.{singular}_repository import {class_name}Repository
from schemas.{singular}_schema import {class_name}Create, {class_name}Read, {class_name}Update
from models.models import {class_name}
from services.interfaces import ICRUDService


class {class_name}Service(ICRUDService[{class_name}Read, {class_name}Create, {class_name}Update]):
    """Service for {class_name} domain logic implementing segregated CRUD interfaces."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = {class_name}Repository(db)

    # ICreateService
    def create(self, data: {class_name}Create) -> {class_name}Read:
        """Create a new {class_name}."""
        obj = self.repository.create(**data.model_dump())
        return {class_name}Read.model_validate(obj)

    # IReadService
    def get_by_id(self, id: int) -> Optional[{class_name}Read]:
        """Get a single {class_name} by ID."""
        obj = self.repository.get_by_id(id)
        if not obj:
            return None
        return {class_name}Read.model_validate(obj)

    def get_all(self) -> List[{class_name}Read]:
        """Get all {class_name}s."""
        objs = self.repository.get_all()
        return [{class_name}Read.model_validate(obj) for obj in objs]

    # IUpdateService
    def update(self, id: int, data: {class_name}Update) -> Optional[{class_name}Read]:
        """Update a {class_name}."""
        update_data = data.model_dump(exclude_unset=True)
        obj = self.repository.update(id, **update_data)
        if not obj:
            return None
        return {class_name}Read.model_validate(obj)

    # IDeleteService
    def delete(self, id: int) -> bool:
        """Delete a {class_name}."""
        return self.repository.delete(id)

    # ISearchService
    def search(self, **filters) -> List[{class_name}Read]:
        """Search {class_name}s by filters."""
        objs = self.repository.search(**filters)
        return [{class_name}Read.model_validate(obj) for obj in objs]

    def count(self, **filters) -> int:
        """Count {class_name}s matching filters."""
        return self.repository.count(**filters)
'''

ROUTER_TEMPLATE = '''"""Router for {class_name} endpoints following ISP - Dependency Inversion Principle."""
from flask import Blueprint, request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from flask_babel import _

from schemas.{singular}_schema import {class_name}Create, {class_name}Update
from services.{singular}_service import {class_name}Service
from services.interfaces import IReadService, ICreateService, IUpdateService, IDeleteService
from db.database import get_db
from services.response_service import Response


router = Blueprint('{plural}', __name__)
name = "{plural}"


# Dependency Injection - Each endpoint depends only on what it needs
def _get_create_service(db: Session) -> ICreateService:
    """Inject only create interface (ISP)."""
    return {class_name}Service(db)


def _get_read_service(db: Session) -> IReadService:
    """Inject only read interface (ISP)."""
    return {class_name}Service(db)


def _get_update_service(db: Session) -> IUpdateService:
    """Inject only update interface (ISP)."""
    return {class_name}Service(db)


def _get_delete_service(db: Session) -> IDeleteService:
    """Inject only delete interface (ISP)."""
    return {class_name}Service(db)


@router.post("/{plural}")
def create():
    """Create a new {class_name}."""
    db: Session = next(get_db())

    try:
        data = {class_name}Create.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: ICreateService = _get_create_service(db)
        result = service.create(data)
        return Response._ok_data(result.model_dump(), _("{upper}_CREATED"), 201, name)
    except ValueError as e:
        return Response._error(_("INVALID_DATA"), str(e), 400, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{plural}/<int:id>")
def get_by_id(id):
    """Get a single {class_name} by ID."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        result = service.get_by_id(id)

        if not result:
            return Response._error(_("{upper}_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("{upper}_FOUND"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.get("/{plural}")
def list_all():
    """Get all {class_name}s."""
    db: Session = next(get_db())

    try:
        service: IReadService = _get_read_service(db)
        results = service.get_all()

        return Response._ok_data(
            [r.model_dump() for r in results],
            _("{upper}_LIST"),
            200,
            name
        )
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.patch("/{plural}/<int:id>")
def update(id):
    """Update a {class_name}."""
    db: Session = next(get_db())

    try:
        data = {class_name}Update.model_validate(request.json)
    except ValidationError as e:
        return Response._error(_("VALIDATION_ERROR"), e.errors(), 400, name)

    try:
        service: IUpdateService = _get_update_service(db)
        result = service.update(id, data)

        if not result:
            return Response._error(_("{upper}_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_data(result.model_dump(), _("{upper}_UPDATED"), 200, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)


@router.delete("/{plural}/<int:id>")
def delete(id):
    """Delete a {class_name}."""
    db: Session = next(get_db())

    try:
        service: IDeleteService = _get_delete_service(db)
        success = service.delete(id)

        if not success:
            return Response._error(_("{upper}_NOT_FOUND"), _("NONE"), 404, name)

        return Response._ok_message(_("{upper}_DELETED"), 204, name)
    except Exception as e:
        return Response._error(_("DATABASE_ERROR"), str(e), 500, name)
'''


def generate_code():
    """Generate all repositories, services and routers."""
    api_path = Path("/home/miguel/src/economy/api")

    for entity in ENTITIES:
        class_name = entity["class"]
        singular = entity["singular"]
        plural = entity["plural"]
        upper = singular.upper()

        # Skip Expense (already done)
        if class_name == "Expense":
            continue

        print(f"\n{'='*80}")
        print(f"Generating code for {class_name}")
        print('='*80)

        # Generate repository code
        repo_code = REPOSITORY_TEMPLATE.format(class_name=class_name)
        repo_file = api_path / "repositories" / f"{singular}_repository.py"
        print(f"Repository: {repo_file}")

        # Generate service code
        service_code = SERVICE_TEMPLATE.format(
            class_name=class_name,
            singular=singular,
        )
        service_file = api_path / "services" / f"{singular}_service.py"
        print(f"Service: {service_file}")

        # Generate router code
        router_code = ROUTER_TEMPLATE.format(
            class_name=class_name,
            singular=singular,
            plural=plural,
            upper=upper,
        )
        router_file = api_path / "routers" / f"{singular}_router.py"
        print(f"Router: {router_file}")

        print(f"\n{class_name} Repository code:\n{repo_code}")
        print(f"\n{class_name} Service code:\n{service_code}")
        print(f"\n{class_name} Router code:\n{router_code}")


if __name__ == "__main__":
    generate_code()
