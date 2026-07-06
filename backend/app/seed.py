# app/seed.py
"""One-off script that loads seed data from all registered sources into the DB.

Run manually after `alembic upgrade head`:

    python -m app.seed
"""
import logging

from app.database import SessionLocal
from app.models import Risk
from app.sources import load_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed() -> None:
    records = load_all()
    if not records:
        logger.warning("No records returned by sources, nothing to seed.")
        return

    sources = {r["source"] for r in records}
    db = SessionLocal()
    try:
        deleted = (
            db.query(Risk)
            .filter(Risk.source.in_(sources))
            .delete(synchronize_session=False)
        )
        db.bulk_insert_mappings(Risk, records)
        db.commit()
        logger.info("Removed %d old record(s), inserted %d new record(s).", deleted, len(records))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
