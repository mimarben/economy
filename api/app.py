from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError

from config import DevelopmentConfig, get_config
from db.database import init_db
from routers import register_routers
from services.core.response_service import Response
from services.logs.logger_service import setup_logger
from utils.i18n import reset_locale, set_locale


logger = setup_logger("main")


def create_app(config_class=None) -> FastAPI:
    config_class = config_class or get_config()
    validator = getattr(config_class, "validate", None)
    if callable(validator):
        validator()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if getattr(config_class, "INIT_DB_ON_STARTUP", False):
            init_db()
        yield

    app = FastAPI(title="Economy API", lifespan=lifespan)
    cors = getattr(config_class, "CORS", DevelopmentConfig.CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors["origins"],
        allow_methods=cors["methods"],
        allow_headers=cors["allow_headers"],
    )

    @app.middleware("http")
    async def select_locale(request: Request, call_next):
        language = request.query_params.get("lang")
        if not language:
            accepted_languages = request.headers.get("accept-language", "")
            language = "es" if accepted_languages.lower().startswith("es") else "en"
        locale_token = set_locale(language)
        try:
            return await call_next(request)
        finally:
            reset_locale(locale_token)

    @app.get("/health", tags=["system"])
    def health_check():
        return {"status": "ok"}

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_request: Request, error: RequestValidationError):
        return Response.error("VALIDATION_ERROR", error.errors(), 400, "main")

    @app.exception_handler(HTTPException)
    async def handle_http_error(_request: Request, error: HTTPException):
        detail_key = error.detail if isinstance(error.detail, str) else "HTTP_ERROR"
        return Response.error(
            detail_key,
            detail_key,
            error.status_code,
            "main",
            headers=error.headers,
        )

    @app.exception_handler(Exception)
    async def handle_exception(_request: Request, error: Exception):
        logger.exception("Unhandled exception")
        if isinstance(error, SQLAlchemyTimeoutError):
            return Response.error(
                "DATABASE_ERROR",
                "DB_CONNECTION_TIMEOUT",
                500,
                "main",
            )
        return Response.error("INTERNAL_ERROR", "UNEXPECTED_ERROR", 500, "main")

    register_routers(app, url_prefix=getattr(config_class, "PREFIX", "/api"))
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=DevelopmentConfig.HOST,
        port=DevelopmentConfig.PORT,
        reload=DevelopmentConfig.DEBUG,
    )
