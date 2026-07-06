# app/sources/manager_excel.py
import logging
import re
from datetime import datetime
import zoneinfo
from urllib.parse import parse_qs, unquote, urlparse

import pandas as pd
import requests
from openlocationcode import openlocationcode as olc

from app.sources.base import DataSource

logger = logging.getLogger(__name__)

# Approximate centroid of Gmina Reńska Wieś (powiat kędzierzyńsko-kozielski),
# where every location in the sheet lies. Used as the reference point to
# recover the shortened Plus Codes found in the "Koordynaty" column.
REFERENCE_LAT = 50.35
REFERENCE_LNG = 18.17

DEFAULT_WEIGHT = 1
VERIFIED_STATUS = "zweryfikowane"

_PLACE_COORD_RE = re.compile(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)")
_MAP_VIEW_COORD_RE = re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)")

_COLUMNS = ["lp", "kategoria", "obiekt", "solectwo", "adres", "koordynaty", "rodzaj_zagrozenia"]


class ExcelMapaZagrozenSource(DataSource):
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
        df = df.drop(columns=["lp"])
        for col in df.columns:
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
        df = df[df["kategoria"].notna()]
        return df.reset_index(drop=True)

    def geocode(self, cleaned: pd.DataFrame) -> pd.DataFrame:
        df = cleaned.copy()
        coords = df["koordynaty"].apply(self._resolve_coordinates)
        df["lat"] = coords.apply(lambda c: c[0])
        df["lng"] = coords.apply(lambda c: c[1])
        return df

    def map_to_schema(self, geocoded: pd.DataFrame) -> list[dict]:
        timezone = zoneinfo.ZoneInfo("Europe/Warsaw");
        now = datetime.now(tz=timezone)
        records = []
        for row in geocoded.itertuples():
            if pd.isna(row.lat) or pd.isna(row.lng):
                logger.warning("Skipping row without resolvable coordinates: %s", row.rodzaj_zagrozenia)
                continue
            risk_type = row.rodzaj_zagrozenia
            if isinstance(row.obiekt, str) and row.obiekt:
                risk_type = f"{row.obiekt} – {risk_type}"
            records.append({
                "kategoria_glowna": row.kategoria,
                "typ_ryzyka": risk_type,
                "lat": round(row.lat, 7),
                "lng": round(row.lng, 7),
                "waga": DEFAULT_WEIGHT,
                "zrodlo": self.name,
                "status": VERIFIED_STATUS,
                "data_aktualizacji": now,
            })
        return records

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
