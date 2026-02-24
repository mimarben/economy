from .users.user_router import router as user_router
from .expenses.expense_router import router as expense_router
from .expenses.expense_category_router import router as expense_category_router
from .households.household_router import router as household_router
from .households.household_member_router import router as household_member_router
from .incomes.income_category_router import router as income_category_router
from .incomes.income_router import router as income_router
from .finance.source_router import router as source_router
from .savings.saving_router import router as saving_router
from .finance.account_router import router as account_router
from .investments.investment_router import router as investment_router
from .investments.investment_category_router import router as investment_category_router
from .finance.bank_router import router as bank_router
from .savings.saving_log_router import router as saving_log_router
from .investments.investment_log_router import router as investment_log_router
from .summaries.financial_summary_router import router as financial_summary_router
from .ai.transactions_ai_router import router as transactions_ai_router
from .core.system_router import router as core_router

def register_blueprints(app, url_prefix=""):
    blueprints = [
        user_router,expense_router, expense_category_router,
        household_router, household_member_router, income_category_router,
        income_router, source_router, saving_router, account_router, investment_router,
        investment_category_router, bank_router, saving_log_router, investment_log_router,
        financial_summary_router, transactions_ai_router, core_router
    ]
    for bp in blueprints:
        app.register_blueprint(bp, url_prefix=url_prefix)
