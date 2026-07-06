import logging
from pathlib import Path

from app.sources.manager_excel import ExcelMapaZagrozenSource

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# Single registration point for all data sources. Adding a new source
# (an API, another file) only means adding an entry here.
SOURCES = [
    ExcelMapaZagrozenSource(file_path=str(DATA_DIR / "Mapa zagrożeń.xlsx")),
]


def load_all() -> list[dict]:
    """Run every registered source. A failure in one does not stop the others."""
    records: list[dict] = []
    for source in SOURCES:
        try:
            records.extend(source.run())
        except Exception:
            logger.exception("Failed to load source '%s'", source.name)
    return records
