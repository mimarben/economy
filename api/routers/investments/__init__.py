from .investment_router import router as investment_router, name as investment_name
from .investment_category_router import router as investment_category_router, name as investment_category_name
from .investment_log_router import router as investment_log_router, name as investment_log_name
from .market_quote_router import router as market_quote_router, name as market_quote_name

# New routers for Increment 2
from .instrument_router import router as instrument_router, name as instrument_name
from .instrument_composition_router import router as instrument_composition_router, name as instrument_composition_name

__all__ = [
    # Existing
    'investment_router', 'investment_name',
    'investment_category_router', 'investment_category_name',
    'investment_log_router', 'investment_log_name',
    'market_quote_router', 'market_quote_name',
    # New for Increment 2
    'instrument_router', 'instrument_name',
    'instrument_composition_router', 'instrument_composition_name',
]
