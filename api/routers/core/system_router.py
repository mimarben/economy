from flask import Blueprint
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db
from services.core.response_service import Response
from flask_babel import _

router = Blueprint("core", __name__)
name = "core"

@router.get("/core/db-info")
def get_db_info():
    """
    Get database engine information.

    Infrastructure endpoint.
    """
    db: Session = next(get_db())

    try:
        engine = db.get_bind()
        dialect = engine.dialect.name

        if dialect == "postgresql":
            version = db.execute(text("SELECT version()")).scalar()
        elif dialect == "mysql":
            version = db.execute(text("SELECT VERSION()")).scalar()
        elif dialect == "sqlite":
            version = db.execute(text("SELECT sqlite_version()")).scalar()
        else:
            version = "Unknown"

        return Response._ok_data(
            {
                "dialect": dialect,
                "driver": engine.dialect.driver,
                "version": version
            },
            _("DB_INFO"),
            200,
            name
        )

    except Exception as e:
        return Response._error(
            _("DATABASE_ERROR"),
            str(e),
            500,
            name
        )
