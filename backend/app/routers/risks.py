from datetime import datetime
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

from fastapi import Query

import hmac

router = APIRouter(prefix="/risks", tags=["risks"])


def verify_admin(x_admin_key: str = Header(...)):
    expected = os.getenv("ADMIN_API_KEY")
    if not expected or not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/", response_model=list[schemas.RiskOut])
def get_risks(
    hazard_category: list[schemas.HazardCategory] | None = Query(default=None),
    status: schemas.RiskStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Risk)

    if hazard_category:
        query = query.filter(models.Risk.hazard_category.in_(hazard_category))
    if status is not None:
        query = query.filter(models.Risk.status == status)

    return query.all()


@router.post("/", response_model=schemas.RiskOut, status_code=201)
def create_risk(risk: schemas.RiskCreate, db: Session = Depends(get_db)):
    new_risk = models.Risk(
        **risk.model_dump(),
        status=models.RiskStatus.PENDING,
        updated_at=datetime.utcnow(),
    )
    db.add(new_risk)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nie udało się zapisać zgłoszenia")
    db.refresh(new_risk)
    return new_risk

@router.patch("/{risk_id}", response_model=schemas.RiskOut, dependencies=[Depends(verify_admin)])
def update_risk(risk_id: int, risk_update: schemas.RiskUpdate, db: Session = Depends(get_db)):
    risk = db.get(models.Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    update_data = risk_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(risk, key, value)
    
    risk.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(risk)
    return risk

@router.patch("/{risk_id}/approve", response_model=schemas.RiskOut, dependencies=[Depends(verify_admin)])
def approve_risk(risk_id: int, db: Session = Depends(get_db)):
    risk = db.get(models.Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    risk.status = models.RiskStatus.VERIFIED
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Nie udało się zatwierdzić zgłoszenia")
    db.refresh(risk)
    return risk


@router.delete("/{risk_id}", dependencies=[Depends(verify_admin)])
def delete_risk(risk_id: int, db: Session = Depends(get_db)):
    risk = db.get(models.Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404)
    db.delete(risk)
    db.commit()
    return {"status": "deleted"}