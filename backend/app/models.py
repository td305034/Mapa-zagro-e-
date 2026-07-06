# app/models.py
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Zagrozenie(Base):
    __tablename__ = "zagrozenia"

    id = Column(Integer, primary_key=True)
    kategoria_glowna = Column(String, nullable=False)
    typ_ryzyka = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    waga = Column(Integer, default=1)
    zrodlo = Column(String)
    status = Column(String, default="niezweryfikowane")
    data_aktualizacji = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))