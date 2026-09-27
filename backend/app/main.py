"""Application entry point."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.seed import seed_database
from app.api import auth, buildings, categories, rooms, businesses, search, upload

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.APP_NAME, version="1.0.0")

origins = [item.strip() for item in settings.CORS_ORIGINS.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

upload_dir = Path(settings.UPLOAD_ROOT)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=upload_dir), name="static")

@app.on_event("startup")
def startup() -> None:
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router, prefix="/api")
app.include_router(buildings.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")
app.include_router(businesses.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
