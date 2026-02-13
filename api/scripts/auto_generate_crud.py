#!/usr/bin/env python3
"""Auto-generate all remaining services and repositories."""

from pathlib import Path

REPO_TEMPLATE = '''"""Repository for {class_name} entity following segregated interfaces."""
from repositories.base_repository import BaseRepository
from models import {class_name}


class {class_name}Repository(BaseRepository[{class_name}]):
    """Repository for {class_name} with custom queries."""

    def __init__(self, db):
        super().__init__(db, {class_name})
'''

SERVICE_TEMPLATE = '''"""Service for {class_name} implementing segregated CRUD interfaces."""
from typing import Optional, List
from sqlalchemy.orm import Session
from repositories.{singular}_repository import {class_name}Repository
from schemas.{singular}_schema import {class_name}Create, {class_name}Read, {class_name}Update
from models import {class_name}
from services.interfaces import ICRUDService


class {class_name}Service(ICRUDService[{class_name}Read, {class_name}Create, {class_name}Update]):
    """Service for {class_name} implementing segregated CRUD interfaces."""

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

# All entities that need service/repo
ENTITIES = [
    {"class": "ExpensesCategory", "singular": "expense_category"},
    {"class": "IncomesCategory", "singular": "income_category"},
    {"class": "Income", "singular": "income"},
    {"class": "Saving", "singular": "saving"},
    {"class": "SavingLog", "singular": "saving_log"},
    {"class": "InvestmentsCategory", "singular": "investment_category"},
    {"class": "Investment", "singular": "investment"},
    {"class": "InvestmentLog", "singular": "investment_log"},
    {"class": "FinancialSummary", "singular": "financial_summary"},
    {"class": "Household", "singular": "household"},
    {"class": "HouseholdMember", "singular": "household_member"},
]

# Skip already done
SKIP = ["Expense", "User", "Bank", "Account", "Source"]

api_path = Path("/home/miguel/src/economy/api")

for entity in ENTITIES:
    class_name = entity["class"]
    singular = entity["singular"]

    # Skip if already created
    repo_file = api_path / "repositories" / f"{singular}_repository.py"
    service_file = api_path / "services" / f"{singular}_service.py"

    # Generate repository
    if not repo_file.exists():
        repo_code = REPO_TEMPLATE.format(class_name=class_name)
        repo_file.write_text(repo_code)
        print(f"✅ Created {repo_file.name}")
    else:
        print(f"⏭️  Skipped {repo_file.name} (exists)")

    # Generate service
    if not service_file.exists():
        service_code = SERVICE_TEMPLATE.format(
            class_name=class_name,
            singular=singular,
        )
        service_file.write_text(service_code)
        print(f"✅ Created {service_file.name}")
    else:
        print(f"⏭️  Skipped {service_file.name} (exists)")

print("\n✅ All services and repositories generated!")
