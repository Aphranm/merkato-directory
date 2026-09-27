from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth import get_current_admin
from app.database import get_db
from app.models import Building, Category
from app.schemas import BuildingCreate, BuildingUpdate

router = APIRouter(prefix="/buildings", tags=["buildings"])

def public_building(building):
    categories = []
    for category in building.categories:
        if not category.is_published or not building.is_published:
            continue
        categories.append({
            "id": category.id, "name": category.name, "description": category.description,
            "image_url": category.image_url, "sort_order": category.sort_order,
            "is_published": category.is_published,
            "room_count": sum(1 for room in category.rooms if room.is_published),
        })
    return {"id": building.id, "name": building.name, "description": building.description,
            "image_url": building.image_url, "sort_order": building.sort_order,
            "is_published": building.is_published, "category_count": len(categories),
            "categories": categories}

@router.get("")
def list_buildings(db: Session = Depends(get_db)):
    return [public_building(item) for item in db.query(Building).filter(Building.is_published.is_(True)).order_by(Building.sort_order, Building.id).all()]

@router.get("/{building_id}")
def get_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id, Building.is_published.is_(True)).first()
    if not building: raise HTTPException(404, "Building not found")
    result = public_building(building)
    result["categories"] = []
    for category in building.categories:
        if not category.is_published: continue
        rooms = [{"id": r.id, "room_number": r.room_number, "name": r.name, "description": r.description,
                  "image_url": r.image_url, "sort_order": r.sort_order, "is_published": r.is_published}
                 for r in category.rooms if r.is_published]
        result["categories"].append({"id": category.id, "name": category.name, "description": category.description,
            "image_url": category.image_url, "sort_order": category.sort_order, "is_published": category.is_published,
            "room_count": len(rooms), "rooms": rooms})
    return result

@router.post("", status_code=status.HTTP_201_CREATED)
def create_building(payload: BuildingCreate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = Building(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item

@router.put("/{building_id}")
def update_building(building_id: int, payload: BuildingUpdate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Building).filter(Building.id == building_id).first()
    if not item: raise HTTPException(404, "Building not found")
    for key, value in payload.model_dump().items(): setattr(item, key, value)
    db.commit(); db.refresh(item); return item

@router.delete("/{building_id}")
def delete_building(building_id: int, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    item = db.query(Building).filter(Building.id == building_id).first()
    if not item: raise HTTPException(404, "Building not found")
    children = sum(len(c.rooms) for c in item.categories)
    businesses = sum(1 for c in item.categories for r in c.rooms if r.business)
    categories = len(item.categories)
    db.delete(item); db.commit()
    return {"success": True, "deleted": {"categories": categories, "rooms": children, "businesses": businesses}}

@router.get("/{building_id}/categories")
def list_categories(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id, Building.is_published.is_(True)).first()
    if not building: raise HTTPException(404, "Building not found")
    return [{"id": c.id, "building_id": c.building_id, "name": c.name, "description": c.description,
             "image_url": c.image_url, "sort_order": c.sort_order, "is_published": c.is_published}
            for c in building.categories if c.is_published]

@router.post("/{building_id}/categories", status_code=status.HTTP_201_CREATED)
def create_category(building_id: int, payload: CategoryCreate, db: Session = Depends(get_db), _: object = Depends(get_current_admin)):
    if not db.query(Building).filter(Building.id == building_id).first(): raise HTTPException(404, "Building not found")
    item = Category(building_id=building_id, **payload.model_dump()); db.add(item); db.commit(); db.refresh(item); return item
