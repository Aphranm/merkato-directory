from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Business, Floor
from app.schemas import BusinessOut
from app.services.directory import serialize_business

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.get("", response_model=list[BusinessOut])
def list_businesses(db: Session = Depends(get_db)):
    businesses = db.scalars(
        select(Business)
        .where(Business.status == "active")
        .options(
            selectinload(Business.categories),
            selectinload(Business.floor).selectinload(Floor.building),
        )
        .order_by(Business.name.asc())
    ).all()
    return [serialize_business(business) for business in businesses]


@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business or business.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return serialize_business(business)
