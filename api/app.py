# app.py
from flask import Flask, request
from flask_babel import Babel, gettext

from config import Config, DevelopmentConfig
from api.routers.user_router import router as user_router
from api.routers.place_router import router as place_router


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

# Run app (optional if using a separate runner)
if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])