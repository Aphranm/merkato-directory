from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_admin
from app.database import get_db
from app.models import Room, Business
from app.schemas import BusinessCreate, BusinessUpdate

router = APIRouter(prefix="/businesses", tags=["businesses"])

@router.get("/{business_id}")
def get_business(business_id: int, db: Session = Depends(get_db)):
    item = db.query(Business).filter(Business.id == business_id, Business.is_published.is_(True)).first()
    if not item: raise HTTPException(404, "Business not found")
    return {"id": item.id, "room_id": item.room_id, "business_name": item.business_name, "description": item.description,
            "phone": item.phone, "alternative_phone": item.alternative_phone, "telegram": item.telegram,
            "whatsapp": item.whatsapp, "facebook": item.facebook, "instagram": item.instagram, "website": item.website,
            "opening_hours": item.opening_hours, "services": item.services, "products": item.products, "notes": item.notes,
            "image_url": item.image_url, "gallery_images": item.gallery_images or [],
            "room": {"id": item.room.id, "room_number": item.room.room_number, "name": item.room.name,
                     "category": {"id": item.room.category.id, "name": item.room.category.name,
                                  "building": {"id": item.room.category.building.id, "name": item.room.category.building.name}}}}

@router.post("/room/{room_id}", status_code=status.HTTP_201_CREATED)
def create_business(room_id: int, payload: BusinessCreate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room: raise HTTPException(404, "Room not found")
    if room.business: raise HTTPException(409, "This room already has a business")
    item = Business(room_id=room_id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.put("/{business_id}")
def update_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Business).filter(Business.id == business_id).first()
    if not item: raise HTTPException(404, "Business not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/{business_id}")
def delete_business(business_id: int, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Business).filter(Business.id == business_id).first()
    if not item: raise HTTPException(404, "Business not found")
    db.delete(item); db.commit(); return {"success": True}
