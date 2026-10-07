from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
def list_reports(db: Session = Depends(get_db), _admin: object = Depends(require_admin)):
    return db.scalars(select(Report).order_by(Report.created_at.desc())).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_report(
    payload: dict,
    db: Session = Depends(get_db),
):
    report = Report(
        business_id=payload.get("business_id"),
        entity_type=payload.get("entity_type", "business"),
        entity_id=payload.get("entity_id"),
        reason=payload.get("reason", "other"),
        message=payload.get("message"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
