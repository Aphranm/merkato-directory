from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import AuditLog

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
def list_audit_logs(db: Session = Depends(get_db), _admin: object = Depends(require_admin)):
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc())).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_audit_log(payload: dict, db: Session = Depends(get_db), _admin: object = Depends(require_admin)):
    item = AuditLog(
        entity_type=payload.get("entity_type", "business"),
        entity_id=payload.get("entity_id"),
        actor_id=payload.get("actor_id"),
        action=payload.get("action", "updated"),
        details=payload.get("details"),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
