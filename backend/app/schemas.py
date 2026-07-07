from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    lat: float
    lng: float
    weight: int = Field(default=1, ge=1, le=5)


    @field_validator("main_category")
    @classmethod
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError("Kategoria nie może być pusta")
        return v.strip()


class RiskCreate(RiskBase):
    lat: float
    lng: float

    @model_validator(mode="after")
    def validate_location_in_powiat(self):
        if not (50.16 <= self.lat <= 50.43) or not (17.9 <= self.lng <= 18.55):
            raise ValueError("Zagrożenie powinno znajdować się w powiecie kędzierzyńsko-kozielskim.")
        self.lat = round(self.lat, 7)
        self.lng = round(self.lng, 7)
        return self

class RiskOut(RiskBase):
    id: int
    source: str | None = None
    status: RiskStatus
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RiskUpdate(BaseModel):
    main_category: str | None = None
    risk_type: str | None = None
    lat: float | None = Field(default=None, ge=50.16, le=50.43)
    lng: float | None = Field(default=None, ge=17.9, le=18.55)
    weight: int | None = Field(default=None, ge=1, le=5)
    source: str | None = None