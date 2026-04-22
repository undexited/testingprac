from pathlib import Path
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def _sqlite_path_from_url(database_url: str) -> str | None:
    if not database_url.startswith("sqlite:///"):
        return None
    raw = database_url.replace("sqlite:///", "", 1)
    if raw.startswith("./"):
        raw = raw[2:]
    return str(Path(raw))


def ensure_sqlite_compatibility() -> None:
    db_path = _sqlite_path_from_url(settings.database_url)
    if not db_path:
        return

    if db_path.startswith("file:"):
        return

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    tables = {row[0] for row in cur.execute("select name from sqlite_master where type='table'").fetchall()}

    def column_names(table: str) -> set[str]:
        return {row[1] for row in cur.execute(f"pragma table_info({table})").fetchall()}

    if "users" in tables:
        cols = column_names("users")
        if "is_admin" not in cols:
            cur.execute("alter table users add column is_admin INTEGER NOT NULL DEFAULT 0")

    if "conversations" in tables:
        cols = column_names("conversations")
        if "workspace_id" not in cols:
            cur.execute("alter table conversations add column workspace_id INTEGER DEFAULT 1")

    if "messages" in tables:
        cols = column_names("messages")
        if "provider" not in cols:
            cur.execute("alter table messages add column provider TEXT DEFAULT 'builtin'")
        if "model" not in cols:
            cur.execute("alter table messages add column model TEXT DEFAULT ''")
        if "latency_ms" not in cols:
            cur.execute("alter table messages add column latency_ms INTEGER DEFAULT 0")

    if "login_events" in tables:
        cols = column_names("login_events")
        if "status" not in cols:
            cur.execute("alter table login_events add column status TEXT DEFAULT 'success'")
        if "ip_address" not in cols:
            cur.execute("alter table login_events add column ip_address TEXT DEFAULT ''")
        if "user_agent" not in cols:
            cur.execute("alter table login_events add column user_agent TEXT DEFAULT ''")

    conn.commit()
    conn.close()
