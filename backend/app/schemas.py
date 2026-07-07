from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import HazardCategory


class RiskStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class RiskBase(BaseModel):

    main_category: str
    risk_type: str
    hazard_category: HazardCategory
    address: str | None = None
    lat: float = Field(ge=49.9, le=50.5, description="Szerokość geograficzna w granicach powiatu")
    lng: float = Field(ge=17.8, le=18.5, description="Długość geograficzna w granicach powiatu")
    weight: int = Field(default=1, ge=1, le=5)


    @field_validator("main_category")
    @classmethod
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError("Kategoria nie może być pusta")
        return v.strip()
    
    @field_validator("lat", "lng")
    @classmethod
    def round_coordinates(cls, v):
        return round(v, 7)


class RiskCreate(RiskBase):

    pass


class RiskOut(RiskBase):
    id: int
    source: str | None = None
    status: RiskStatus
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RiskUpdate(BaseModel):
    main_category: str | None = None
    risk_type: str | None = None
    lat: float | None = Field(default=None, ge=49.9, le=50.5)
    lng: float | None = Field(default=None, ge=17.8, le=18.5)
    weight: int | None = Field(default=None, ge=1, le=5)
    source: str | None = None