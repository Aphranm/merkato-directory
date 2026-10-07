from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Building, Floor
from app.schemas import BuildingOut, FloorOut

router = APIRouter(prefix="/api/buildings", tags=["buildings"])


@router.get("", response_model=list[BuildingOut])
def list_buildings(db: Session = Depends(get_db)):
    buildings = db.scalars(
        select(Building).where(Building.status == "active").order_by(Building.name.asc())
    ).all()
    return buildings


@router.get("/{building_id}/floors", response_model=list[FloorOut])
def list_building_floors(building_id: int, db: Session = Depends(get_db)):
    building = db.get(Building, building_id)
    if building is None or building.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    return db.scalars(
        select(Floor)
        .where(Floor.building_id == building_id, Floor.status == "active")
        .order_by(Floor.floor_number.asc())
    ).all()


@router.get("/{building_id}", response_model=BuildingOut)
def get_building(building_id: int, db: Session = Depends(get_db)):
    building = db.get(Building, building_id)
    if not building or building.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    return building


