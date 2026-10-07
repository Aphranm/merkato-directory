from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Business, Building, Category, Floor
from app.services.directory import serialize_business

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search_businesses(
    q: str | None = Query(default=None, max_length=120),
    building_id: int | None = None,
    floor_id: int | None = None,
    category_id: int | None = None,
    building: str | None = None,
    category: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        select(Business)
        .join(Floor, Business.floor_id == Floor.id)
        .join(Building, Floor.building_id == Building.id)
        .where(
            Business.status == "active",
            Floor.status == "active",
            Building.status == "active",
        )
    )

    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Business.name.ilike(search_term),
                Business.description.ilike(search_term),
                Business.short_description.ilike(search_term),
                Business.phone.ilike(search_term),
                Business.whatsapp.ilike(search_term),
            )
        )

    if building_id is not None:
        building_record = db.get(Building, building_id)
        if building_record is None or building_record.status != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
        query = query.where(Floor.building_id == building_id)

    if floor_id is not None:
        floor_record = db.get(Floor, floor_id)
        if floor_record is None or floor_record.status != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
        if building_id is not None and floor_record.building_id != building_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Floor does not belong to the selected building",
            )
        query = query.where(Business.floor_id == floor_id)

    if category_id is not None:
        category_record = db.get(Category, category_id)
        if category_record is None or category_record.status != "active":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        query = query.where(Business.categories.any(Category.id == category_id))
    elif category:
        category_term = f"%{category.strip()}%"
        query = query.where(
            Business.categories.any(
                or_(Category.name.ilike(category_term), Category.slug.ilike(category_term))
            )
        )

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    results = db.scalars(
        query.options(
            selectinload(Business.images),
            selectinload(Business.categories),
            selectinload(Business.floor).selectinload(Floor.building),
        )
        .order_by(Business.name.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return {
        "query": q,
        "page": page,
        "limit": limit,
        "total": total,
        "results": [
            {
                **serialize_business(business),
                "images": [
                    {
                        "file_url": image.file_url,
                        "alt_text": image.alt_text,
                        "is_primary": image.is_primary,
                    }
                    for image in sorted(
                        business.images,
                        key=lambda image: (not image.is_primary, image.sort_order, image.id),
                    )
                ],
            }
            for business in results
        ],
    }
