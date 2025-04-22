from .user_router import router as user_router
from .place_router import router as place_router
from .expense_router import router as expense_router
from .expense_category_router import router as expense_category_router
from .household_router import router as household_router
from .household_member_router import router as household_member_router
from .income_category_router import router as income_category_router
from .income_router import router as income_router
from .source_router import router as source_router
from .saving_router import router as saving_router
from .account_router import router as account_router

def register_blueprints(app):
    blueprints = [
        user_router, place_router, expense_router, expense_category_router,
        household_router, household_member_router, income_category_router,
        income_router, source_router, saving_router, account_router
    ]
    for bp in blueprints:
        app.register_blueprint(bp)