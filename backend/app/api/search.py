from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Business, Room, Category, Building

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def search_directory(q: str = Query("", max_length=100), limit: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    terms = [term for term in q.strip().lower().split() if term]
    if not terms: return []
    query = db.query(Business).join(Room).join(Category).join(Building).filter(
        Business.is_published.is_(True), Room.is_published.is_(True), Category.is_published.is_(True), Building.is_published.is_(True))
    filters = []
    for term in terms:
        pattern = f"%{term}%"
        filters.append(or_(Business.business_name.ilike(pattern), Business.description.ilike(pattern), Business.phone.ilike(pattern),
            Business.alternative_phone.ilike(pattern), Business.services.ilike(pattern), Business.products.ilike(pattern),
            Business.notes.ilike(pattern), Room.name.ilike(pattern), Room.room_number.ilike(pattern), Category.name.ilike(pattern), Building.name.ilike(pattern)))
    results = []
    for item in query.filter(and_(*filters)).order_by(Business.business_name).limit(limit).all():
        room, category, building = item.room, item.room.category, item.room.category.building
        results.append({"id": item.id, "business_name": item.business_name, "phone": item.phone, "image_url": item.image_url,
            "room": {"id": room.id, "room_number": room.room_number, "name": room.name},
            "category": {"id": category.id, "name": category.name}, "building": {"id": building.id, "name": building.name}})
    return results
