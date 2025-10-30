from .user_router import router as user_router
from .expense_router import router as expense_router
from .expense_category_router import router as expense_category_router
from .household_router import router as household_router
from .household_member_router import router as household_member_router
from .income_category_router import router as income_category_router
from .income_router import router as income_router
from .source_router import router as source_router
from .saving_router import router as saving_router
from .account_router import router as account_router
from .investment_router import router as investment_router
from .investment_category_router import router as investment_category_router
from .bank_router import router as bank_router
from .saving_log_router import router as saving_log_router
from .investment_log_router import router as investment_log_router
from .financial_summary_router import router as financial_summary_router


def register_blueprints(app, url_prefix=""):
    blueprints = [
        user_router,expense_router, expense_category_router,
        household_router, household_member_router, income_category_router,
        income_router, source_router, saving_router, account_router, investment_router,
        investment_category_router, bank_router, saving_log_router, investment_log_router,
        financial_summary_router
    ]
    for bp in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)
