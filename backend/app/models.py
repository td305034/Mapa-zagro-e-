# app/models.py
from datetime import datetime, timezone
import enum

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RiskStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

STATUS_WEIGHTS = {
    RiskStatus.PENDING: 2,
    RiskStatus.VERIFIED: 5,
    RiskStatus.REJECTED: 1,
}

class HazardCategory(str, enum.Enum):
    FIRE = "fire"
    TRAFFIC = "traffic"
    FLOOD = "flood"
    STRUCTURAL = "structural"
    ENVIRONMENTAL = "environmental"
    CRIME = "crime"
    CRITICAL_SUPPLY = "critical_supply"

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True)
    main_category = Column(String, nullable=False)
    risk_type = Column(String, nullable=False)
    hazard_category = Column(SQLEnum(HazardCategory), nullable=True)
    address = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    weight = Column(Integer, default=1)
    source = Column(String)
    status = Column(SQLEnum(RiskStatus), default=RiskStatus.PENDING)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))