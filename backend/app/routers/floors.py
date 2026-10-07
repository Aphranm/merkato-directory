from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Building, Business, Category, Floor
from app.schemas import BusinessOut, FloorOut
from app.services.directory import serialize_business

router = APIRouter(prefix="/api/floors", tags=["floors"])


@router.get("", response_model=list[FloorOut])
def list_floors(building_id: int | None = Query(default=None), db: Session = Depends(get_db)):
    query = select(Floor).join(Building).where(
        Floor.status == "active",
        Building.status == "active",
    )
    if building_id is not None:
        building = db.get(Building, building_id)
        if building is None or building.status != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
        query = query.where(Floor.building_id == building_id)
    return db.scalars(query.order_by(Floor.floor_number.asc())).all()


@router.get("/{floor_id}", response_model=FloorOut)
def get_floor(floor_id: int, db: Session = Depends(get_db)):
    floor = db.get(Floor, floor_id)
    if not floor or floor.status != "active" or floor.building.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    return floor


@router.get("/{floor_id}/businesses", response_model=list[BusinessOut])
def list_floor_businesses(floor_id: int, db: Session = Depends(get_db)):
    floor = db.get(Floor, floor_id)
    if floor is None or floor.status != "active" or floor.building.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    businesses = db.scalars(
        select(Business)
        .where(Business.floor_id == floor_id, Business.status == "active")
        .options(
            selectinload(Business.categories),
            selectinload(Business.floor).selectinload(Floor.building),
        )
        .order_by(Business.name.asc())
    ).all()
    return [serialize_business(business) for business in businesses]


