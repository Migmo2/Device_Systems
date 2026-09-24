"""Dependencia de sesion de base de datos para FastAPI."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.connection import get_db


def database_session() -> Generator[Session, None, None]:
    yield from get_db()
