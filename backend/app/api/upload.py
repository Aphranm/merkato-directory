import time
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.auth import get_current_admin
from app.config import settings
from app.schemas import UploadResponse
from app.utils.images import sanitize_filename, validate_image_file, optimize_image

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), _: object = Depends(get_current_admin)):
    content = await file.read()
    valid, message = validate_image_file(file.filename or "", len(content))
    if not valid: raise HTTPException(400, message)
    try: optimized, ext = optimize_image(content)
    except Exception: raise HTTPException(400, "Invalid or unreadable image")
    name = sanitize_filename(file.filename or "image")
    stem = Path(name).stem or "image"
    filename = f"{stem}_{int(time.time() * 1000)}.{ext}"
    directory = Path(settings.UPLOAD_ROOT); directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_bytes(optimized)
    return {"url": f"{settings.APP_PUBLIC_URL.rstrip('/')}/static/{filename}", "filename": filename}
