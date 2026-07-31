"""Unit tests for CategorizationService (rules-first + optional AI fallback).

Uses the designed ``ai_service`` injection seam: a tiny stub stands in for the AI
categorizer. Real CategoryRule/SourceRule rows are seeded into in-memory SQLite
(no mocking of repositories), matching the suite's no-mock convention.
"""
import pytest

from models import (
    CategoryRule,
    Source,
    SourceRule,
    SourceTypeEnum,
    TransactionEnum,
)
from services.rules.categorization_service import CategorizationService


class _FakeAiService:
    """Minimal stand-in matching the ``ai_service.categorize(desc, type)`` shape."""

    def __init__(self, category_id=None, raise_exc=None):
        self._category_id = category_id
        self._raise_exc = raise_exc
        self.calls = []

    def categorize(self, description, transaction_type):
        self.calls.append((description, transaction_type))
        if self._raise_exc:
            raise self._raise_exc
        return self._category_id


def _seed_rule(db_session, *, pattern, category_id, type_=TransactionEnum.EXPENSE,
               priority=100, active=True, ignore=False):
    rule = CategoryRule(
        name=f"rule-{pattern}",
        pattern=pattern,
        type=type_,
        priority=priority,
        is_active=active,
        ignore_in_analysis=ignore,
        category_id=category_id,
    )
    db_session.add(rule)
    db_session.commit()
    return rule


# ────────────────────────── categorize_transaction ──────────────────────────

def test_categorize_matches_rule_returns_category(db_session):
    _seed_rule(db_session, pattern="mercado", category_id=10)
    service = CategorizationService(db_session)

    assert service.categorize_transaction("Compra en MERCADONA", "expense") == 10


def test_categorize_priority_higher_wins(db_session):
    _seed_rule(db_session, pattern="compra", category_id=1, priority=10)
    _seed_rule(db_session, pattern="compra", category_id=2, priority=100)
    service = CategorizationService(db_session)

    # both match; rules are evaluated priority DESC → category 2 wins
    assert service.categorize_transaction("compra algo", "expense") == 2


def test_categorize_inactive_rule_ignored(db_session):
    _seed_rule(db_session, pattern="mercado", category_id=10, active=False)
    service = CategorizationService(db_session)

    assert service.categorize_transaction("Compra en MERCADONA", "expense") is None


def test_categorize_no_match_without_ai_returns_none(db_session):
    _seed_rule(db_session, pattern="nada", category_id=10)
    service = CategorizationService(db_session)  # no ai_service

    assert service.categorize_transaction("algo sin regla", "expense") is None


def test_categorize_ai_fallback_used(db_session):
    service = CategorizationService(db_session, ai_service=_FakeAiService(category_id=77))

    assert service.categorize_transaction("algo sin regla", "expense") == 77


def test_categorize_ai_exception_swallowed_returns_none(db_session):
    service = CategorizationService(
        db_session, ai_service=_FakeAiService(raise_exc=RuntimeError("boom"))
    )

    assert service.categorize_transaction("algo sin regla", "expense") is None


def test_categorize_invalid_type_returns_none(db_session):
    service = CategorizationService(db_session)

    assert service.categorize_transaction("algo", "not-a-type") is None


def test_categorize_empty_description_returns_none(db_session):
    service = CategorizationService(db_session)

    assert service.categorize_transaction("", "expense") is None


# ─────────────────────── categorize_transaction_with_flags ───────────────────────

def test_categorize_with_flags_returns_category_source_and_ignore(db_session):
    source = Source(name="Supermarket", description="Groceries", active=True,
                    type=SourceTypeEnum.EXPENSE)
    db_session.add(source)
    db_session.commit()

    _seed_rule(db_session, pattern="mercadona", category_id=10, ignore=True)
    db_session.add(SourceRule(
        name="sr-mercadona", pattern="mercadona", type=TransactionEnum.EXPENSE,
        priority=100, is_active=True, source_id=source.id,
    ))
    db_session.commit()

    result = CategorizationService(db_session).categorize_transaction_with_flags(
        "Compra MERCADONA", "expense"
    )

    assert result == {"category_id": 10, "source_id": source.id, "ignore_in_analysis": True}


def test_categorize_with_flags_no_match_returns_empty_bucket(db_session):
    service = CategorizationService(db_session)

    result = service.categorize_transaction_with_flags("nada que coincida", "expense")

    assert result == {"category_id": None, "source_id": None, "ignore_in_analysis": False}
