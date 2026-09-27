from sqlalchemy.orm import Session
from app.models import AdminUser, Building
from app.auth import hash_password

def seed_database(db: Session) -> None:
    if db.query(AdminUser).filter(AdminUser.username == "admin").first(): return
    from app.config import settings
    admin = AdminUser(username=settings.ADMIN_USERNAME, password=hash_password(settings.ADMIN_PASSWORD), role="admin")
    db.add(admin)
    db.commit()
    if not db.query(Building).first():
        seed_building = Building(name="Sample Building", description="This is a sample building to get you started.", is_published=True, sort_order=0)
        db.add(seed_building)
        db.commit()
