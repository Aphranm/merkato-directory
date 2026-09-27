from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_admin
from app.database import get_db
from app.models import Building, Category
from app.schemas import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

def public_category(item):
    rooms = [{"id": r.id, "room_number": r.room_number, "name": r.name, "description": r.description,
              "image_url": r.image_url, "sort_order": r.sort_order, "is_published": r.is_published}
             for r in item.rooms if r.is_published]
    return {"id": item.id, "building_id": item.building_id, "name": item.name, "description": item.description,
            "image_url": item.image_url, "sort_order": item.sort_order, "is_published": item.is_published,
            "building_name": item.building.name, "room_count": len(rooms), "rooms": rooms}

@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    item = db.query(Category).join(Building).filter(Category.id == category_id, Category.is_published.is_(True), Building.is_published.is_(True)).first()
    if not item: raise HTTPException(404, "Category not found")
    return public_category(item)

@router.post("/building/{building_id}", status_code=status.HTTP_201_CREATED)
def create_category_compat(building_id: int, payload: CategoryCreate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    if not db.query(Building).filter(Building.id == building_id).first(): raise HTTPException(404, "Building not found")
    item = Category(building_id=building_id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.put("/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Category).filter(Category.id == category_id).first()
    if not item: raise HTTPException(404, "Category not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Category).filter(Category.id == category_id).first()
    if not item: raise HTTPException(404, "Category not found")
    counts = {"rooms": len(item.rooms), "businesses": sum(1 for r in item.rooms if r.business)}
    db.delete(item); db.commit(); return {"success": True, "deleted": counts}

@router.get("/{category_id}/rooms")
def list_rooms(category_id: int, db: Session = Depends(get_db)):
    item = db.query(Category).filter(Category.id == category_id, Category.is_published.is_(True)).first()
    if not item: raise HTTPException(404, "Category not found")
    return [{"id": r.id, "category_id": r.category_id, "room_number": r.room_number, "name": r.name,
             "description": r.description, "image_url": r.image_url, "sort_order": r.sort_order,
             "is_published": r.is_published} for r in item.rooms if r.is_published]

@router.post("/{category_id}/rooms", status_code=status.HTTP_201_CREATED)
def create_room_compat(category_id: int, payload, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    # Kept as a compatibility route; the typed implementation is in rooms.py.
    from app.models import Room
    if not db.query(Category).filter(Category.id == category_id).first(): raise HTTPException(404, "Category not found")
    item = Room(category_id=category_id, **payload.model_dump(exclude={"category_id"})); db.add(item); db.commit(); db.refresh(item); return item
