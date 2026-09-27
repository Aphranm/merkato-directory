import io
import os
from PIL import Image
from app.config import settings

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}

def validate_image_file(filename: str, size: int):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS: return False, "Unsupported image type. Use JPG, PNG, WEBP, or GIF."
    if size <= 0 or size > settings.MAX_UPLOAD_SIZE: return False, "Image is empty or exceeds the upload size limit."
    return True, ""

def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    return os.path.splitext(filename)[0][:50] if filename else "image"

def optimize_image(content: bytes):
    image = Image.open(io.BytesIO(content))
    image.load()
    if image.mode not in ("RGB", "RGBA"): image = image.convert("RGBA")
    image.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format="WEBP", quality=84, method=6)
    return output.getvalue(), "webp"
