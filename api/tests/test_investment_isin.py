"""ISIN support on Investment: schema validation and persistence.

Covers the new optional `isin` column end to end at the unit level:
Pydantic normalization/validation, persistence through the existing
InvestmentService, and the /meta contract (the Angular form is generated
from it, so the field must show up there).
"""
from datetime import date

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from models import Investment
from schemas.investments.investment_schema import InvestmentBase, InvestmentCreate, InvestmentUpdate
from schemas.core.export_schema import export_schema
from services.investments.investment_service import InvestmentService


VALID_ISIN = "IE00B83YJG36"


def _payload(**overrides) -> dict:
    payload = {
        "description": "iShares Developed Real Estate",
        "date": date(2026, 11, 18),
        "currency": "EUR",
        "amount": "1000.00",
        "account_id": 1,
        "category_id": 1,
    }
    payload.update(overrides)
    return payload


class TestIsinValidation:
    def test_valid_isin_accepted(self):
        investment = InvestmentCreate(**_payload(isin=VALID_ISIN))
        assert investment.isin == VALID_ISIN

    def test_isin_normalized_to_uppercase(self):
        investment = InvestmentCreate(**_payload(isin="ie00b83yjg36"))
        assert investment.isin == VALID_ISIN

    def test_isin_surrounding_spaces_stripped(self):
        investment = InvestmentCreate(**_payload(isin=f" {VALID_ISIN} "))
        assert investment.isin == VALID_ISIN

    def test_missing_isin_still_valid(self):
        """Backwards compatibility: existing payloads without ISIN keep working."""
        investment = InvestmentCreate(**_payload())
        assert investment.isin is None

    def test_empty_string_becomes_none(self):
        investment = InvestmentCreate(**_payload(isin=""))
        assert investment.isin is None

    @pytest.mark.parametrize("bad_isin", [
        "IE00B83YJG3",       # 11 chars
        "IE00B83YJG367",     # 13 chars
        "12X00B83YJG3",      # country code must be letters
        "IE00B83YJG3A",      # check digit must be numeric
    ])
    def test_invalid_isin_rejected(self, bad_isin):
        with pytest.raises(ValidationError):
            InvestmentCreate(**_payload(isin=bad_isin))

    def test_update_accepts_and_clears_isin(self):
        assert InvestmentUpdate(**{"isin": VALID_ISIN}).isin == VALID_ISIN
        update = InvestmentUpdate.model_validate({"isin": None})
        assert update.model_dump(exclude_unset=True) == {"isin": None}


class TestIsinPersistence:
    def test_create_persists_isin(self, db_session):
        service = InvestmentService(db_session)
        result = service.create(InvestmentCreate(**_payload(isin=VALID_ISIN)))
        assert result.isin == VALID_ISIN

        stmt = select(Investment).where(Investment.id == result.id)
        stored = db_session.execute(stmt).scalars().one()
        assert stored.isin == VALID_ISIN

    def test_update_changes_isin(self, db_session):
        service = InvestmentService(db_session)
        created = service.create(InvestmentCreate(**_payload(isin=VALID_ISIN)))

        updated = service.update(created.id, InvestmentUpdate(**{"isin": "LU0996175948"}))
        assert updated.isin == "LU0996175948"

    def test_dedup_unchanged_by_isin(self, db_session):
        """Two entries for the same ISIN must coexist (recurring contributions).

        The dedup hash only covers date/amount/description/account, so only
        the ISIN differing must NOT make two rows collide. (The friendly
        DUPLICATE_TRANSACTION ValueError relies on Postgres reporting the
        constraint name, which SQLite does not, so we assert on the
        IntegrityError itself here.)
        """
        from sqlalchemy.exc import IntegrityError

        service = InvestmentService(db_session)
        first = service.create(InvestmentCreate(**_payload(isin=VALID_ISIN)))

        with pytest.raises(IntegrityError):
            service.create(InvestmentCreate(**_payload(isin=VALID_ISIN)))

        second = service.create(InvestmentCreate(
            **_payload(isin=VALID_ISIN, date=date(2026, 11, 19), amount="500.00")
        ))
        assert second.id != first.id
        assert second.isin == first.isin == VALID_ISIN


class TestMetaContract:
    def test_meta_includes_isin_field(self):
        """The Angular form is metadata-driven: isin must be exported."""
        meta = export_schema(InvestmentBase)
        assert "isin" in {f["key"] for f in meta["fields"]}
