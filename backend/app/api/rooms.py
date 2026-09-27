from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_admin
from app.database import get_db
from app.models import Category, Room
from app.schemas import RoomCreate, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"])

def room_public(item):
    business = item.business
    data = None
    if business and business.is_published:
        data = {k: getattr(business, k) for k in ("id", "business_name", "description", "phone", "alternative_phone", "telegram", "whatsapp", "facebook", "instagram", "website", "opening_hours", "services", "products", "notes", "image_url", "gallery_images")}
        data["gallery_images"] = data["gallery_images"] or []
    return {"id": item.id, "category_id": item.category_id, "room_number": item.room_number, "name": item.name,
            "description": item.description, "image_url": item.image_url, "sort_order": item.sort_order,
            "is_published": item.is_published, "building_name": item.category.building.name,
            "category_name": item.category.name, "business": data}

@router.get("/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    item = db.query(Room).filter(Room.id == room_id, Room.is_published.is_(True)).first()
    if not item: raise HTTPException(404, "Room not found")
    return room_public(item)

@router.post("/category/{category_id}", status_code=status.HTTP_201_CREATED)
def create_room(category_id: int, payload: RoomCreate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    if not db.query(Category).filter(Category.id == category_id).first(): raise HTTPException(404, "Category not found")
    item = Room(category_id=category_id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.put("/{room_id}")
def update_room(room_id: int, payload: RoomUpdate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Room).filter(Room.id == room_id).first()
    if not item: raise HTTPException(404, "Room not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Room).filter(Room.id == room_id).first()
    if not item: raise HTTPException(404, "Room not found")
    db.delete(item); db.commit(); return {"success": True}

@router.get("/{room_id}/business")
def room_business(room_id: int, db: Session = Depends(get_db)):
    item = db.query(Room).filter(Room.id == room_id, Room.is_published.is_(True)).first()
    if not item: raise HTTPException(404, "Room not found")
    return item.business if item.business and item.business.is_published else None
