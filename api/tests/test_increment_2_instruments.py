"""Tests for Increment 2: Instruments, Identifiers, Compositions and Search.

Covers:
- InstrumentService/Repository CRUD and search (by ISIN, name, ticker, provider identifier)
- Attach existing investments to instruments
- InstrumentComposition CRUD (informational only, does not affect totals)
- ManagedPortfolio can be created without identifiers
- Ambiguous search results return all matches (no auto-selection)
"""
from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy import select

from models import Investment, Instrument, InstrumentIdentifier, InstrumentComposition
from schemas.investments.instrument_schema import InstrumentCreate, InstrumentUpdate
from schemas.investments.instrument_identifier_schema import InstrumentIdentifierCreate
from schemas.investments.instrument_composition_schema import InstrumentCompositionCreate
from services.investments.instrument_service import InstrumentService
from services.investments.instrument_composition_service import InstrumentCompositionService
from services.investments.investment_service import InvestmentService
from schemas.investments.investment_schema import InvestmentCreate as InvestmentCreateSchema


ISIN_A = "IE00B83YJG36"
ISIN_B = "LU0996175948"
TICKER_A = "VNQ"
PROVIDER_ID = "myinvestor-12345"


class TestInstrumentCRUD:
    """Test Instrument CRUD operations."""

    def test_create_instrument_with_identifiers(self, db_session):
        """Create an instrument with ISIN and ticker identifiers."""
        service = InstrumentService(db_session)
        
        # Create instrument with identifiers
        instrument_data = InstrumentCreate(
            name="iShares Developed Real Estate",
            description="ETF that tracks real estate index",
            asset_class="ETF",
            category_id=1,
            currency="EUR",
            is_active=True,
        )
        instrument = service.create(instrument_data)
        
        # Add ISIN identifier
        identifier = InstrumentIdentifier(
            instrument_id=instrument.id,
            identifier_type="ISIN",
            value=ISIN_A,
            is_primary=True,
        )
        db_session.add(identifier)
        db_session.commit()
        
        # Verify
        stmt = select(Instrument).where(Instrument.id == instrument.id)
        stored = db_session.execute(stmt).scalars().one()
        assert stored.name == "iShares Developed Real Estate"
        assert stored.asset_class == "ETF"

    def test_create_managed_portfolio_without_identifiers(self, db_session):
        """ManagedPortfolio can be created without any identifiers."""
        service = InstrumentService(db_session)
        
        # Create a managed portfolio without any identifiers
        instrument_data = InstrumentCreate(
            name="Cartera Gestionada MyInvestor",
            description="Cartera gestionada automáticamente",
            asset_class="MANAGED_PORTFOLIO",
            category_id=1,
            currency="EUR",
            is_active=True,
        )
        instrument = service.create(instrument_data)
        
        # Verify it was created without identifiers
        stmt = select(Instrument).where(Instrument.id == instrument.id)
        stored = db_session.execute(stmt).scalars().one()
        assert stored.asset_class == "MANAGED_PORTFOLIO"
        
        # Verify no identifiers
        stmt_id = select(InstrumentIdentifier).where(
            InstrumentIdentifier.instrument_id == instrument.id
        )
        identifiers = db_session.execute(stmt_id).scalars().all()
        assert len(identifiers) == 0

    def test_update_instrument(self, db_session):
        """Update an existing instrument."""
        service = InstrumentService(db_session)
        
        # Create instrument
        instrument_data = InstrumentCreate(
            name="Original Name",
            asset_class="ETF",
            category_id=1,
            currency="EUR",
        )
        instrument = service.create(instrument_data)
        
        # Update it
        update_data = InstrumentUpdate(
            name="Updated Name",
            description="Updated description",
        )
        updated = service.update(instrument.id, update_data)
        
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"


class TestInstrumentSearch:
    """Test instrument search by various criteria."""

    def test_search_by_isin(self, db_session):
        """Search instruments by ISIN identifier."""
        # Create instrument with ISIN
        service = InstrumentService(db_session)
        instrument_data = InstrumentCreate(
            name="Test Instrument",
            asset_class="ETF",
            category_id=1,
            currency="EUR",
        )
        instrument = service.create(instrument_data)
        
        # Add ISIN identifier
        identifier = InstrumentIdentifier(
            instrument_id=instrument.id,
            identifier_type="ISIN",
            value=ISIN_A,
            is_primary=True,
        )
        db_session.add(identifier)
        db_session.commit()
        
        # Search by ISIN
        results = service.search_by_isin(ISIN_A)
        assert len(results) == 1
        assert results[0].id == instrument.id

    def test_search_by_name(self, db_session):
        """Search instruments by name (partial match)."""
        service = InstrumentService(db_session)
        
        # Create instruments
        for name in ["Test Fund A", "Test Fund B", "Other Fund"]:
            instrument_data = InstrumentCreate(
                name=name,
                asset_class="FUND",
                category_id=1,
                currency="EUR",
            )
            service.create(instrument_data)
        
        # Search by partial name
        results = service.search_by_name("Test")
        assert len(results) == 2

    def test_search_by_ticker(self, db_session):
        """Search instruments by ticker identifier."""
        service = InstrumentService(db_session)
        instrument_data = InstrumentCreate(
            name="Test Stock",
            asset_class="STOCK",
            category_id=1,
            currency="USD",
        )
        instrument = service.create(instrument_data)
        
        # Add ticker identifier
        identifier = InstrumentIdentifier(
            instrument_id=instrument.id,
            identifier_type="TICKER",
            value=TICKER_A,
            is_primary=True,
        )
        db_session.add(identifier)
        db_session.commit()
        
        # Search by ticker
        results = service.search_by_ticker(TICKER_A)
        assert len(results) == 1
        assert results[0].id == instrument.id

    def test_search_by_provider_identifier(self, db_session):
        """Search instruments by provider identifier."""
        service = InstrumentService(db_session)
        instrument_data = InstrumentCreate(
            name="Provider Fund",
            asset_class="FUND",
            category_id=1,
            currency="EUR",
        )
        instrument = service.create(instrument_data)
        
        # Add provider identifier
        identifier = InstrumentIdentifier(
            instrument_id=instrument.id,
            identifier_type="PROVIDER",
            value=PROVIDER_ID,
            provider="myinvestor",
            is_primary=True,
        )
        db_session.add(identifier)
        db_session.commit()
        
        # Search by provider and identifier
        results = service.search_by_provider_identifier("myinvestor", PROVIDER_ID)
        assert len(results) == 1
        assert results[0].id == instrument.id

    def test_ambiguous_search_returns_all(self, db_session):
        """Ambiguous search (e.g., 'Bitcoin') should return all matches, not auto-select."""
        service = InstrumentService(db_session)
        
        # Create multiple instruments with similar names
        for name in ["Bitcoin", "Bitcoin Fund", "Bitcoin ETF"]:
            instrument_data = InstrumentCreate(
                name=name,
                asset_class="CRYPTO",
                category_id=1,
                currency="USD",
            )
            service.create(instrument_data)
        
        # Search by partial name
        results = service.search_by_name("Bitcoin")
        assert len(results) == 3, "Should return all matches, not auto-select one"


class TestAttachInvestment:
    """Test attaching existing investments to instruments."""

    def test_attach_investment_to_instrument(self, db_session):
        """Attach an existing investment to an instrument."""
        # Create investment first
        investment_service = InvestmentService(db_session)
        
        # Create investment without instrument
        inv_data = InvestmentCreateSchema(
            description="Test Investment",
            date=date(2026, 11, 20),
            currency="EUR",
            amount=Decimal("1000.00"),
            account_id=1,
            category_id=1,
        )
        investment = investment_service.create(inv_data)
        assert investment.instrument_id is None
        
        # Create instrument
        instrument_service = InstrumentService(db_session)
        instrument_data = InstrumentCreate(
            name="Test Instrument",
            asset_class="ETF",
            category_id=1,
            currency="EUR",
        )
        instrument = instrument_service.create(instrument_data)
        
        # Attach investment to instrument
        result = instrument_service.attach_investment(instrument.id, investment.id)
        assert result is not None
        
        # Verify investment now has instrument_id
        stmt = select(Investment).where(Investment.id == investment.id)
        updated_investment = db_session.execute(stmt).scalars().one()
        assert updated_investment.instrument_id == instrument.id


class TestInstrumentComposition:
    """Test InstrumentComposition CRUD (informational only)."""

    def test_create_composition(self, db_session):
        """Create a composition (parent-child relationship)."""
        service = InstrumentCompositionService(db_session)
        
        # Create parent instrument (fund)
        instrument_service = InstrumentService(db_session)
        parent_data = InstrumentCreate(
            name="Parent Fund",
            asset_class="FUND",
            category_id=1,
            currency="EUR",
        )
        parent = instrument_service.create(parent_data)
        
        # Create child instrument (stock)
        child_data = InstrumentCreate(
            name="Child Stock",
            asset_class="STOCK",
            category_id=1,
            currency="USD",
        )
        child = instrument_service.create(child_data)
        
        # Create composition
        comp_data = InstrumentCompositionCreate(
            parent_instrument_id=parent.id,
            child_instrument_id=child.id,
            quantity=10.5,
            weight=0.25,
            source="myinvestor",
            deleted_at=None,
        )
        result = service.create(comp_data)
        
        assert result.parent_instrument_id == parent.id
        assert result.child_instrument_id == child.id
        assert result.quantity == 10.5
        assert result.weight == 0.25

    def test_composition_does_not_affect_totals(self, db_session):
        """Compositions are informational only and should not affect investment totals."""
        investment_service = InvestmentService(db_session)
        instrument_service = InstrumentService(db_session)
        composition_service = InstrumentCompositionService(db_session)
        
        # Create investment
        inv_data = InvestmentCreateSchema(
            description="Test Investment",
            date=date(2026, 11, 20),
            currency="EUR",
            amount=Decimal("1000.00"),
            account_id=1,
            category_id=1,
        )
        investment = investment_service.create(inv_data)
        initial_total = investment.amount
        
        # Create instrument and attach investment
        instrument_data = InstrumentCreate(
            name="Test Instrument",
            asset_class="ETF",
            category_id=1,
            currency="EUR",
        )
        instrument = instrument_service.create(instrument_data)
        instrument_service.attach_investment(instrument.id, investment.id)
        
        # Create composition (should not affect total)
        child_data = InstrumentCreate(
            name="Child",
            asset_class="STOCK",
            category_id=1,
            currency="EUR",
        )
        child = instrument_service.create(child_data)
        
        comp_data = InstrumentCompositionCreate(
            parent_instrument_id=instrument.id,
            child_instrument_id=child.id,
            quantity=5.0,
            weight=0.1,
        )
        composition_service.create(comp_data)
        
        # Verify investment total unchanged
        stmt = select(Investment).where(Investment.id == investment.id)
        updated = db_session.execute(stmt).scalars().one()
        assert updated.amount == initial_total

    def test_get_composition_by_parent(self, db_session):
        """Get all compositions for a parent instrument."""
        composition_service = InstrumentCompositionService(db_session)
        instrument_service = InstrumentService(db_session)
        
        # Create parent
        parent_data = InstrumentCreate(
            name="Parent Fund",
            asset_class="FUND",
            category_id=1,
            currency="EUR",
        )
        parent = instrument_service.create(parent_data)
        
        # Create multiple children
        children = []
        for i in range(3):
            child_data = InstrumentCreate(
                name=f"Child {i}",
                asset_class="STOCK",
                category_id=1,
                currency="EUR",
            )
            child = instrument_service.create(child_data)
            children.append(child)
            
            comp_data = InstrumentCompositionCreate(
                parent_instrument_id=parent.id,
                child_instrument_id=child.id,
                quantity=float(i + 1),
                weight=0.1 * (i + 1),
            )
            composition_service.create(comp_data)
        
        # Get compositions by parent
        compositions = composition_service.get_by_parent(parent.id)
        assert len(compositions) == 3
