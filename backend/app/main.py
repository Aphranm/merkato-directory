from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import SessionLocal, get_db, init_db
from app.models import Role
from app.routers import admin, audit_logs, auth, businesses, buildings, categories, floors, images, reports, search, users, verification

app = FastAPI(
    title="Merkato Directory API",
    version="0.1.0",
    description="Backend API for the Merkato Directory system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


def seed_default_roles():
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            db.add_all(
                [
                    Role(name="super_admin", permissions="all"),
                    Role(name="admin", permissions="building,category,business,report,user"),
                    Role(name="editor", permissions="building,category,business"),
                    Role(name="moderator", permissions="report,verification"),
                    Role(name="viewer", permissions="read"),
                ]
            )
            db.commit()
    finally:
        db.close()


seed_default_roles()

app.mount("/uploads", StaticFiles(directory=images.UPLOADS_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(buildings.router)
app.include_router(floors.router)
app.include_router(categories.router)
app.include_router(businesses.router)
app.include_router(images.router)
app.include_router(images.buildings_router)
app.include_router(reports.router)
app.include_router(verification.router)
app.include_router(users.router)
app.include_router(audit_logs.router)
app.include_router(search.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "api": "ok",
                "database": "unavailable",
                "environment": settings.app_env,
            },
        )
    return {
        "status": "ok",
        "api": "ok",
        "database": "ok",
        "environment": settings.app_env,
    }


@app.get("/")
def root():
    return {
        "message": "Merkato Directory API is running.",
        "version": app.version,
    }
