from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Business, Image, User
from app.schemas import ImageOut

router = APIRouter(prefix="/api/businesses", tags=["business-images"])
buildings_router = APIRouter(prefix="/api/buildings", tags=["building-images"])
UPLOADS_DIR = Path('/tmp/merkato-uploads')
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
MAX_IMAGE_SIZE = 5 * 1024 * 1024
IMAGE_TYPES = {
    "image/jpeg": ("jpg", lambda content: content.startswith(b"\xff\xd8\xff")),
    "image/png": ("png", lambda content: content.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (
        "webp",
        lambda content: content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    ),
}


def serialize_image(image: Image) -> dict:
    return {
        "id": image.id,
        "business_id": image.business_id,
        "file_url": image.file_url,
        "thumbnail_url": image.thumbnail_url,
        "alt_text": image.alt_text,
        "sort_order": image.sort_order,
        "is_primary": image.is_primary,
        "created_at": image.created_at,
    }


@buildings_router.post("/{building_id}/image", status_code=status.HTTP_201_CREATED)
async def upload_building_image(
    building_id: int,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None, max_length=180),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    building = db.get(Building, building_id)
    if building is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")

    image_type = IMAGE_TYPES.get(file.content_type or "")
    if image_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a JPEG, PNG, or WebP image",
        )
    content = await file.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Images must be 5 MB or smaller",
        )
    extension, validate_content = image_type
    if not validate_content(content):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The uploaded file does not match its image type",
        )

    filename = f"{uuid4().hex}.{extension}"
    file_path = UPLOADS_DIR / filename
    file_path.write_bytes(content)
    image_url = f"/uploads/{filename}"
    building.image_url = image_url
    db.add(Image(
        entity_type="building",
        entity_id=building_id,
        file_url=image_url,
        alt_text=alt_text or f"{building.name} building image",
        is_primary=True,
        uploaded_by=admin.id,
    ))
    try:
        db.commit()
    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise
    return {"building_id": building_id, "image_url": image_url}


@router.get("/{business_id}/images", response_model=list[ImageOut])
def list_business_images(business_id: int, db: Session = Depends(get_db)):
    if db.get(Business, business_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    images = db.scalars(
        select(Image)
        .where(Image.business_id == business_id)
        .order_by(Image.is_primary.desc(), Image.sort_order.asc(), Image.id.asc())
    ).all()
    return [serialize_image(image) for image in images]


@router.post(
    "/{business_id}/images",
    response_model=ImageOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_business_image(
    business_id: int,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None, max_length=180),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    business = db.get(Business, business_id)
    if business is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    image_type = IMAGE_TYPES.get(file.content_type or "")
    if image_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a JPEG, PNG, or WebP image",
        )

    content = await file.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Images must be 5 MB or smaller",
        )

    extension, validate_content = image_type
    if not validate_content(content):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The uploaded file does not match its image type",
        )

    image_count = db.scalar(
        select(func.count()).select_from(Image).where(Image.business_id == business_id)
    ) or 0
    filename = f"{uuid4().hex}.{extension}"
    file_path = UPLOADS_DIR / filename
    file_path.write_bytes(content)
    image = Image(
        business_id=business_id,
        entity_type="business",
        entity_id=business_id,
        file_url=f"/uploads/{filename}",
        alt_text=alt_text or f"{business.name} photo",
        sort_order=image_count,
        is_primary=image_count == 0,
        uploaded_by=admin.id,
    )
    db.add(image)
    try:
        db.commit()
        db.refresh(image)
    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise
    return serialize_image(image)


@router.delete("/{business_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_image(
    business_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    image = db.scalar(
        select(Image).where(Image.id == image_id, Image.business_id == business_id)
    )
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    was_primary = image.is_primary
    filename = Path(image.file_url).name
    db.delete(image)
    db.flush()
    if was_primary:
        replacement = db.scalar(
            select(Image)
            .where(Image.business_id == business_id)
            .order_by(Image.sort_order.asc(), Image.id.asc())
        )
        if replacement is not None:
            replacement.is_primary = True
    db.commit()
    (UPLOADS_DIR / filename).unlink(missing_ok=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
