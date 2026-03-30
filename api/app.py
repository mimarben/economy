from flask import Flask, request
from flask_babel import Babel
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError
from flask_jwt_extended import JWTManager, verify_jwt_in_request

from db.database import init_db, remove_db_session
from routers import register_blueprints
from config import DevelopmentConfig
from services.logs.logger_service import setup_logger

load_dotenv()
logger = setup_logger("main")


def _is_public_path(app: Flask, path: str) -> bool:
    public_prefixes = (
        f"{app.config['PREFIX']}/auth",
        f"{app.config['PREFIX']}/system",
    )
    return path.startswith(public_prefixes)


def create_app(config_class=DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    JWTManager(app)

    if app.config.get("INIT_DB_ON_STARTUP", False):
        init_db()

    @app.before_request
    def global_auth():
        if _is_public_path(app, request.path):
            return
        if request.method == "OPTIONS":
            return
        verify_jwt_in_request()

    @app.teardown_appcontext
    def shutdown_session(_exception=None):
        remove_db_session()

    CORS(
        app,
        origins=app.config['CORS']['origins'],
        methods=app.config['CORS']['methods'],
        allow_headers=app.config['CORS']['allow_headers']
    )

    def get_locale():
        return request.args.get('lang') or request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    Babel(app, locale_selector=get_locale)
    register_blueprints(app, url_prefix=app.config['PREFIX'])

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("Unhandled Exception: %s", str(e))
        if isinstance(e, SQLAlchemyTimeoutError):
            return {"error": "Database connection timed out."}, 500
        if isinstance(e, HTTPException):
            return {"error": e.description}, e.code
        return {"error": "An internal error occurred."}, 500

    return app


app = create_app()


if __name__ == "__main__":
    logger.info("Starting the Flask app...")
    logger.info("Configuration loaded for %s:%s", app.config['HOST'], app.config['PORT'])
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
