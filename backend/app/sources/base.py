# app/sources/base.py
from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    """Template Method base class for the data ingestion pipeline.

    Every source (Excel file, future external API, the report form) goes
    through the same fixed sequence of steps: load -> clean -> geocode ->
    map_to_schema. Subclasses only implement the individual steps; `run()`
    fixes their order and the shape of the final output (a list of dicts
    whose keys match the `Zagrozenie` model fields).
    """

    name: str = "unknown"

    def run(self) -> list[dict]:
        raw = self.load()
        cleaned = self.clean(raw)
        geocoded = self.geocode(cleaned)
        return self.map_to_schema(geocoded)

    @abstractmethod
    def load(self) -> Any:
        """Fetch raw data from the source (file, API response, ...)."""

    @abstractmethod
    def clean(self, raw: Any) -> Any:
        """Normalize the raw data: drop empty rows, trim strings, etc."""

    @abstractmethod
    def geocode(self, cleaned: Any) -> Any:
        """Resolve a lat/lng pair for every record."""

    @abstractmethod
    def map_to_schema(self, geocoded: Any) -> list[dict]:
        """Convert records to the common risk schema."""
