from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _migrate(conn):
    """Add new columns / tables to an existing DB without losing data."""
    migrations = [
        "ALTER TABLE uniform_items ADD COLUMN gender VARCHAR(10) DEFAULT 'Both'",
        "CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(bill_date)",
        "ALTER TABLE bills ADD COLUMN payment_mode VARCHAR(10) DEFAULT 'Cash'",
        "ALTER TABLE bills ADD COLUMN upi_transaction_id VARCHAR(100)",
    ]
    for sql in migrations:
        try:
            conn.execute(text(sql))
        except Exception:
            pass  # already applied


def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        _migrate(conn)
    # Ensure one ShopSettings row always exists
    from .models import ShopSettings
    db = SessionLocal()
    try:
        if not db.query(ShopSettings).first():
            db.add(ShopSettings())
            db.commit()
    finally:
        db.close()


def get_shop_settings():
    """Return the single ShopSettings row (always exists after init_db)."""
    from .models import ShopSettings
    db = SessionLocal()
    try:
        s = db.query(ShopSettings).first()
        # detach so callers can use attributes after session closes
        db.expunge(s)
        return s
    finally:
        db.close()


def get_session() -> Session:
    return SessionLocal()
