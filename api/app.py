# app.py
from flask import Flask, request
from flask_babel import Babel, gettext
import os
from dotenv import load_dotenv
import sys



load_dotenv()
pythonpath = os.getenv('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0,pythonpath)
if pythonpath:
    print(f"PYTHONPATH is set to: {pythonpath}")
else:
    print("PYTHONPATH is not set.")

from routers.user_router import router as user_router
from routers.place_router import router as place_router
from routers.expense_router import router as expense_router
from routers.expense_category_router import router as expense_category_router
from routers.household_router import router as household_router

from config import Config, DevelopmentConfig



app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Define the locale selector function
def get_locale():
    # Dynamically select locale based on query parameter or browser preferences
    return request.args.get('lang') or request.accept_languages.best_match(app.config['LANGUAGES'].keys())

# Initialize Babel with locale_selector
babel = Babel(app, locale_selector=get_locale)

# Register route blueprint
app.register_blueprint(user_router)
app.register_blueprint(place_router)
app.register_blueprint(expense_router)
app.register_blueprint(expense_category_router)
app.register_blueprint(household_router)

# Run app (optional if using a separate runner)
if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])