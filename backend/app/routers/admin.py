from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import require_admin
from app.models import AuditLog, Business, Building, Category, Floor, Report, User, Verification
from app.schemas import (
    BusinessCreate,
    BusinessOut,
    BusinessUpdate,
    BuildingCreate,
    BuildingOut,
    BuildingUpdate,
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    FloorCreate,
    FloorOut,
    FloorUpdate,
    ReportUpdate,
    VerificationUpdate,
)
from app.services.directory import serialize_business

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_active_floor(db: Session, floor_id: int) -> Floor:
    floor = db.get(Floor, floor_id)
    if floor is None or floor.status != "active" or floor.building.status != "active":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Choose an active floor")
    return floor


def _require_active_categories(db: Session, category_ids: list[int]) -> list[Category]:
    unique_ids = list(dict.fromkeys(category_ids))
    if not unique_ids:
        return []
    categories = db.scalars(
        select(Category).where(Category.id.in_(unique_ids), Category.status == "active")
    ).all()
    if len(categories) != len(unique_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="One or more categories do not exist or are archived",
        )
    return categories


def _commit_or_conflict(db: Session, detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from error


def _audit(db: Session, admin: User, entity_type: str, entity_id: int, action: str, details: str | None = None) -> None:
    db.add(AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=admin.id,
        action=action,
        details=details,
    ))


def _business_query():
    return select(Business).options(
        selectinload(Business.categories),
        selectinload(Business.floor).selectinload(Floor.building),
    )


@router.get("/buildings", response_model=list[BuildingOut])
def admin_list_buildings(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return db.scalars(select(Building).order_by(Building.name.asc())).all()


@router.post("/buildings", response_model=BuildingOut, status_code=status.HTTP_201_CREATED)
def admin_create_building(
    payload: BuildingCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    building = Building(**payload.model_dump())
    db.add(building)
    db.flush()
    _audit(db, _admin, "building", building.id, "created")
    _commit_or_conflict(db, "A building with this slug already exists")
    db.refresh(building)
    return building


@router.patch("/buildings/{building_id}", response_model=BuildingOut)
def admin_update_building(
    building_id: int,
    payload: BuildingUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    building = db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(building, field, value)
    _audit(db, _admin, "building", building.id, "updated")
    _commit_or_conflict(db, "A building with this slug already exists")
    db.refresh(building)
    return building


@router.delete("/buildings/{building_id}", response_model=BuildingOut)
def admin_archive_building(
    building_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    building = db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    building.status = "archived"
    _audit(db, _admin, "building", building.id, "archived")
    _commit_or_conflict(db, "Building could not be archived")
    return building


@router.get("/floors", response_model=list[FloorOut])
def admin_list_floors(
    building_id: int | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    query = select(Floor).order_by(Floor.building_id.asc(), Floor.floor_number.asc())
    if building_id is not None:
        query = query.where(Floor.building_id == building_id)
    return db.scalars(query).all()


@router.post("/floors", response_model=FloorOut, status_code=status.HTTP_201_CREATED)
def admin_create_floor(
    payload: FloorCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    building = db.get(Building, payload.building_id)
    if building is None or building.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    floor = Floor(**payload.model_dump())
    db.add(floor)
    db.flush()
    _audit(db, _admin, "floor", floor.id, "created")
    _commit_or_conflict(db, "That floor number already exists in this building")
    db.refresh(floor)
    return floor


@router.patch("/floors/{floor_id}", response_model=FloorOut)
def admin_update_floor(
    floor_id: int,
    payload: FloorUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    floor = db.get(Floor, floor_id)
    if floor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    changes = payload.model_dump(exclude_unset=True)
    building_id = changes.get("building_id", floor.building_id)
    building = db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    if building.status != "active" and changes.get("status", floor.status) == "active":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot activate a floor in an archived building")
    if building_id != floor.building_id and db.scalar(
        select(Business.id).where(Business.floor_id == floor_id).limit(1)
    ) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A floor with businesses cannot be moved to another building; relocate the businesses first",
        )
    for field, value in changes.items():
        setattr(floor, field, value)
    _audit(db, _admin, "floor", floor.id, "updated")
    _commit_or_conflict(db, "That floor number already exists in this building")
    db.refresh(floor)
    return floor

@router.delete("/floors/{floor_id}", response_model=FloorOut)
def admin_archive_floor(
    floor_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    floor = db.get(Floor, floor_id)
    if floor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
    active_business = db.scalar(
        select(Business.id).where(Business.floor_id == floor_id, Business.status == "active").limit(1)
    )
    if active_business is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Move or archive businesses on this floor before archiving it",
        )
    floor.status = "archived"
    _audit(db, _admin, "floor", floor.id, "archived")
    _commit_or_conflict(db, "Floor could not be archived")
    return floor


@router.get("/categories", response_model=list[CategoryOut])
def admin_list_categories(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return db.scalars(select(Category).order_by(Category.name.asc())).all()


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def admin_create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    category = Category(**payload.model_dump())
    db.add(category)
    db.flush()
    _audit(db, _admin, "category", category.id, "created")
    _commit_or_conflict(db, "A category with this slug already exists")
    db.refresh(category)
    return category


@router.patch("/categories/{category_id}", response_model=CategoryOut)
def admin_update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    _audit(db, _admin, "category", category.id, "updated")
    _commit_or_conflict(db, "A category with this slug already exists")
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", response_model=CategoryOut)
def admin_archive_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category.status = "archived"
    _audit(db, _admin, "category", category.id, "archived")
    _commit_or_conflict(db, "Category could not be archived")
    return category


@router.get("/businesses", response_model=list[BusinessOut])
def admin_list_businesses(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    businesses = db.scalars(_business_query().order_by(Business.name.asc())).all()
    return [serialize_business(business, include_archived_categories=True) for business in businesses]


@router.post("/businesses", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def admin_create_business(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    floor = _require_active_floor(db, payload.floor_id)
    categories = _require_active_categories(db, payload.category_ids)
    business_data = payload.model_dump(exclude={"category_ids"})
    business = Business(**business_data, floor=floor, categories=categories)
    db.add(business)
    db.flush()
    _audit(db, _admin, "business", business.id, "created")
    _commit_or_conflict(db, "A business with this slug already exists")
    db.refresh(business)
    return serialize_business(business, include_archived_categories=True)


@router.patch("/businesses/{business_id}", response_model=BusinessOut)
def admin_update_business(
    business_id: int,
    payload: BusinessUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    business = db.scalar(_business_query().where(Business.id == business_id))
    if business is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    changes = payload.model_dump(exclude_unset=True)
    if "floor_id" in changes:
        changes["floor"] = _require_active_floor(db, changes.pop("floor_id"))
    if changes.get("status") == "active" and (
        business.floor.status != "active" or business.floor.building.status != "active"
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot activate a business in an archived building or floor",
        )
    if "category_ids" in changes:
        categories = _require_active_categories(db, changes.pop("category_ids"))
        archived_categories = [category for category in business.categories if category.status == "archived"]
        changes["categories"] = categories + archived_categories

    for field, value in changes.items():
        setattr(business, field, value)
    _audit(db, _admin, "business", business.id, "updated")
    _commit_or_conflict(db, "Business update conflicts with an existing record")
    db.refresh(business)
    return serialize_business(business, include_archived_categories=True)


@router.delete("/businesses/{business_id}", response_model=BusinessOut)
def admin_archive_business(
    business_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    business = db.scalar(_business_query().where(Business.id == business_id))
    if business is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    business.status = "archived"
    _audit(db, _admin, "business", business.id, "archived")
    _commit_or_conflict(db, "Business could not be archived")
    return serialize_business(business, include_archived_categories=True)


@router.get("/reports")
def admin_list_reports(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return db.scalars(select(Report).order_by(Report.created_at.desc())).all()


@router.patch("/reports/{report_id}")
def admin_update_report(
    report_id: int,
    payload: ReportUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    report.status = payload.status
    db.add(AuditLog(
        entity_type="report",
        entity_id=report.id,
        actor_id=admin.id,
        action="status_changed",
        details=f"status={payload.status}",
    ))
    _commit_or_conflict(db, "Report could not be updated")
    return report


@router.get("/verifications")
def admin_list_verifications(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return db.scalars(select(Verification).order_by(Verification.created_at.desc())).all()


@router.patch("/verifications/{verification_id}")
def admin_update_verification(
    verification_id: int,
    payload: VerificationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    verification = db.get(Verification, verification_id)
    if verification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification not found")
    verification.status = payload.status
    verification.notes = payload.notes
    db.add(AuditLog(
        entity_type="verification",
        entity_id=verification.id,
        actor_id=admin.id,
        action="status_changed",
        details=f"status={payload.status}",
    ))
    _commit_or_conflict(db, "Verification could not be updated")
    return verification