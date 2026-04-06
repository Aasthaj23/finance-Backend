from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# ── Config ─────────────────────────────────────────────────────────────────────
# Reads from environment variable — falls back to local SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

IS_SQLITE = DATABASE_URL.startswith("sqlite")

# ── Engine ─────────────────────────────────────────────────────────────────────
connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,       # auto-reconnect if DB connection drops
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # log SQL only when needed
)

# Enable FK constraints for SQLite (off by default)
if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ── Session ────────────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # explicit — never auto-commit
    autoflush=False,    # explicit — flush only on commit
)

# ── Base ───────────────────────────────────────────────────────────────────────
Base = declarative_base()


# ── DB Dependency (use in FastAPI routes) ──────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()   # rollback on any unhandled error
        raise
    finally:
        db.close()