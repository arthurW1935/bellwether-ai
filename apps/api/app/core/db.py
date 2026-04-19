from contextlib import contextmanager
from pathlib import Path
import sqlite3

from app.core.config import get_settings


def _sqlite_path() -> Path:
    settings = get_settings()
    prefix = "sqlite:///"
    if not settings.database_url.startswith(prefix):
        raise ValueError("Only sqlite database URLs are supported in this build")

    raw_path = settings.database_url[len(prefix) :]
    path = Path(raw_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(_sqlite_path())
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                domain TEXT NOT NULL,
                headcount INTEGER,
                last_funding TEXT,
                key_execs_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist_entries (
                company_id INTEGER PRIMARY KEY,
                cohort TEXT NOT NULL,
                added_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                taken_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                company_json TEXT NOT NULL,
                cohort TEXT NOT NULL,
                delta_json TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                explanation TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                trace_json TEXT NOT NULL,
                detected_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS brief_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                counts_json TEXT NOT NULL
            )
            """
        )
