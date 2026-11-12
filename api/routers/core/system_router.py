from fastapi import APIRouter, Body, Depends, Query, Request
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db
from services.core.response_service import Response
from utils.i18n import _

router = APIRouter()
name = "core"

@router.get("/core/db-info")
def get_db_info(db: Session = Depends(get_db)):
    """
    Get database engine information.

    Infrastructure endpoint.
    """
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

        return Response.ok_data(
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
        return Response.error(
            _("DATABASE_ERROR"),
            str(e),
            500,
            name
        )
