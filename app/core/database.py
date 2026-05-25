from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Models import
import app.model

# ✅ Create all tables in DB
Base.metadata.create_all(bind=engine)


def _run_compat_migrations():
    """
    Keep existing SQLite DB files compatible with model changes.
    `create_all()` creates missing tables only; it does not add new columns.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as conn:
        user_columns = {
            row[1] for row in conn.exec_driver_sql("PRAGMA table_info('user_list')").fetchall()
        }
        if user_columns and "auth_enabled" not in user_columns:
            conn.exec_driver_sql(
                "ALTER TABLE user_list ADD COLUMN auth_enabled BOOLEAN NOT NULL DEFAULT 0"
            )


_run_compat_migrations()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
