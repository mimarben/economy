from fastapi import Depends, FastAPI
from fastapi.routing import APIRouter

from routers.ai.transactions_ai_router import router as transactions_ai_router
from routers.auth.auth_router import router as auth_router
from routers.cards.card_router import router as card_router
from routers.category_rules.category_rules_router import router as category_rules_router
from routers.category_rules.source_rules_router import router as source_rules_router
from routers.core.system_router import router as core_router
from routers.expenses.expense_category_router import router as expense_category_router
from routers.expenses.expense_router import router as expense_router
from routers.finance.account_router import router as account_router
from routers.finance.bank_router import router as bank_router
from routers.finance.source_router import router as source_router
from routers.households.household_member_router import router as household_member_router
from routers.households.household_router import router as household_router
from routers.imports.import_origin_router import router as import_origin_router
from routers.imports.import_profile_router import router as import_profile_router
from routers.imports.import_router import router as import_router
from routers.incomes.income_category_router import router as income_category_router
from routers.incomes.income_router import router as income_router
from routers.investments.investment_category_router import router as investment_category_router
from routers.investments.investment_log_router import router as investment_log_router
from routers.investments.investment_router import router as investment_router
from routers.investments.market_quote_router import router as market_quote_router
from routers.savings.saving_log_router import router as saving_log_router
from routers.savings.saving_router import router as saving_router
from routers.summaries.summary_router import router as summary_router
from routers.users.user_router import router as user_router
from services.auth.auth_dependencies import require_access_token


_protected_routers: tuple[APIRouter, ...] = (
    user_router,
    expense_router,
    expense_category_router,
    household_router,
    household_member_router,
    income_category_router,
    income_router,
    source_router,
    saving_router,
    account_router,
    investment_router,
    investment_category_router,
    bank_router,
    saving_log_router,
    investment_log_router,
    market_quote_router,
    transactions_ai_router,
    core_router,
    import_router,
    category_rules_router,
    source_rules_router,
    summary_router,
    card_router,
    import_origin_router,
    import_profile_router,
)


def register_routers(app: FastAPI, url_prefix: str = "") -> None:
    for router in _protected_routers:
        app.include_router(
            router,
            prefix=url_prefix,
            dependencies=[Depends(require_access_token)],
        )
    app.include_router(auth_router, prefix=url_prefix)
