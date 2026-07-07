import logging
import re
import time
from datetime import datetime
import zoneinfo
from urllib.parse import parse_qs, unquote, urlparse

import pandas as pd
import requests
from openlocationcode import openlocationcode as olc

from app.models import RiskStatus
from app.sources.base import DataSource
from app.sources.hazard_mapping import get_hazard_category

logger = logging.getLogger(__name__)

REFERENCE_LAT = 50.35
REFERENCE_LNG = 18.17

DEFAULT_WEIGHT = 1
VERIFIED_STATUS = RiskStatus.VERIFIED.value

_PLACE_COORD_RE = re.compile(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)")
_MAP_VIEW_COORD_RE = re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)")

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_USER_AGENT = "mapa-zagrozen-kedzierzynsko-kozielski/1.0"
_NOMINATIM_DELAY_SECONDS = 1.0

_COLUMNS = ["record_number", "main_category", "object_name", "village", "address", "coordinates", "risk_type"]


class ExcelRiskMapSource(DataSource):
    """Adapter for the seed `Mapa zagrożeń.xlsx` file."""

    name = "Mapa zagrożeń.xlsx"

    def __init__(self, file_path: str, sheet_name: str = "Arkusz1"):
        self.file_path = file_path
        self.sheet_name = sheet_name

    def load(self) -> pd.DataFrame:
        return pd.read_excel(self.file_path, sheet_name=self.sheet_name, header=0)

    def clean(self, raw: pd.DataFrame) -> pd.DataFrame:
        df = raw.copy()
        df.columns = _COLUMNS
        df = df.drop(columns=["record_number"])
        for col in df.columns:
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
        df = df[df["main_category"].notna()]
        return df.reset_index(drop=True)

    def geocode(self, cleaned: pd.DataFrame) -> pd.DataFrame:
        df = cleaned.copy()
        resolved = df.apply(self._resolve_row_coordinates, axis=1)
        df["lat"] = resolved.apply(lambda c: c[0])
        df["lng"] = resolved.apply(lambda c: c[1])
        return df

    def map_to_schema(self, geocoded: pd.DataFrame) -> list[dict]:
        timezone = zoneinfo.ZoneInfo("Europe/Warsaw")
        now = datetime.now(tz=timezone)
        records = []
        for row in geocoded.itertuples():
            if pd.isna(row.lat) or pd.isna(row.lng):
                logger.warning(
                    "Skipping row without resolvable coordinates (Plus Code, "
                    "link, and address geocoding all failed): %s",
                    row.risk_type,
                )
                continue

            hazard_category = get_hazard_category(row.risk_type)
            if hazard_category is None:
                raise ValueError(
                    f"No hazard_category mapping for risk_type: '{row.risk_type}' "
                    f"(object: {row.object_name!r}, village: {row.village!r})"
                )

            risk_type = row.risk_type
            if isinstance(row.object_name, str) and row.object_name:
                risk_type = f"{row.object_name} - {risk_type}"

            address = row.address if isinstance(row.address, str) and row.address.strip() else None

            records.append({
                "main_category": row.main_category,
                "hazard_category": hazard_category,
                "risk_type": risk_type,
                "address": address,
                "lat": round(row.lat, 7),
                "lng": round(row.lng, 7),
                "weight": DEFAULT_WEIGHT,
                "source": self.name,
                "status": VERIFIED_STATUS,
                "updated_at": now,
            })
        return records

    def _resolve_row_coordinates(self, row: pd.Series) -> tuple[float | None, float | None]:
        """Try Plus Code / Google Maps link first; fall back to geocoding
        the text address if those are missing or fail to resolve."""
        lat, lng = self._resolve_coordinates(row["coordinates"])
        if lat is not None and lng is not None:
            return lat, lng

        address = row.get("address")
        if isinstance(address, str) and address.strip():
            logger.info(
                "No Plus Code/link for '%s' — falling back to address geocoding: %s",
                row.get("risk_type"), address,
            )
            return self._resolve_address(address, row.get("village"))

        return None, None

    def _resolve_coordinates(self, value) -> tuple[float | None, float | None]:
        if not isinstance(value, str) or not value.strip():
            return None, None
        value = value.strip()
        if value.startswith("http"):
            return self._resolve_google_maps_link(value)
        return self._resolve_plus_code(value)

    def _resolve_google_maps_link(self, url: str) -> tuple[float | None, float | None]:
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            final_url = response.url
        except requests.RequestException:
            logger.warning("Failed to resolve Google Maps link: %s", url)
            return None, None

        if "consent.google.com" in final_url:
            continue_url = parse_qs(urlparse(final_url).query).get("continue")
            if continue_url:
                final_url = unquote(continue_url[0])

        match = _PLACE_COORD_RE.search(final_url) or _MAP_VIEW_COORD_RE.search(final_url)
        if not match:
            logger.warning("No coordinates found in resolved link: %s", final_url)
            return None, None
        return float(match.group(1)), float(match.group(2))

    def _resolve_plus_code(self, value: str) -> tuple[float | None, float | None]:
        code = value.split()[0]
        if not olc.isValid(code):
            logger.warning("Invalid Plus Code: %s", value)
            return None, None
        full_code = olc.recoverNearest(code, REFERENCE_LAT, REFERENCE_LNG) if olc.isShort(code) else code
        area = olc.decode(full_code)
        return area.latitudeCenter, area.longitudeCenter

    def _resolve_address(self, address: str, village) -> tuple[float | None, float | None]:
        query_parts = [address.strip()]
        if isinstance(village, str) and village.strip():
            query_parts.append(village.strip())
        query_parts.append("powiat kędzierzyńsko-kozielski")
        query_parts.append("Polska")
        query = ", ".join(query_parts)

        try:
            response = requests.get(
                _NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": _NOMINATIM_USER_AGENT},
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()
        except requests.RequestException:
            logger.warning("Address geocoding request failed for: %s", query)
            return None, None
        finally:
            time.sleep(_NOMINATIM_DELAY_SECONDS)

        if not results:
            logger.warning("Address geocoding found no results for: %s", query)
            return None, None

        return float(results[0]["lat"]), float(results[0]["lon"])