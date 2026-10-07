from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Verification

router = APIRouter(prefix="/api/verification", tags=["verification"])


@router.get("")
def list_verifications(db: Session = Depends(get_db), _admin: object = Depends(require_admin)):
    return db.scalars(select(Verification).order_by(Verification.created_at.desc())).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_verification(payload: dict, db: Session = Depends(get_db), _admin: object = Depends(require_admin)):
    verification = Verification(
        business_id=payload["business_id"],
        status=payload.get("status", "pending"),
        verified_by=payload.get("verified_by"),
        notes=payload.get("notes"),
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification
