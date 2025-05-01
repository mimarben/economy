# app.py
from flask import Flask, request
from flask_babel import Babel, gettext
import os
from dotenv import load_dotenv
import sys
from werkzeug.exceptions import HTTPException
from flask_cors import CORS



load_dotenv()
pythonpath = os.getenv('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0,pythonpath)


from routers import register_blueprints

from config import Config, DevelopmentConfig

# Setup logging
from services.logger_service import setup_logger
logger = setup_logger("main")


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
CORS(app,
    origins=app.config['CORS']['origins'],
    methods=app.config['CORS']['methods'],
    allow_headers=app.config['CORS']['allow_headers'])


# Define the locale selector function
def get_locale():
    # Dynamically select locale based on query parameter or browser preferences
    return request.args.get('lang') or request.accept_languages.best_match(app.config['LANGUAGES'].keys())

# Initialize Babel with locale_selector
babel = Babel(app, locale_selector=get_locale)

# Register route blueprint
register_blueprints(app, url_prefix=app.config['PREFIX'])


# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception("Unhandled Exception: %s", str(e))
    if isinstance(e, HTTPException):
        return {"error": e.description}, e.code
    return {"error": "An internal error occurred."}, 500


# Run app (optional if using a separate runner)
if __name__ == "__main__":
    logger.info("Starting the Flask app...")
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
