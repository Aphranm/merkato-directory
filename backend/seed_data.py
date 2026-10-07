from app.database import SessionLocal
from app.models import Business, Building, Category, Floor, Role, User
from app.security import hash_password


def seed_demo_data():
    db = SessionLocal()
    try:
        role_ids = {role.name: role.id for role in db.query(Role).all()}
        if not role_ids:
            roles = [
                Role(name="super_admin", permissions="all"),
                Role(name="admin", permissions="building,category,business,report,user"),
                Role(name="editor", permissions="building,category,business"),
                Role(name="moderator", permissions="report,verification"),
                Role(name="viewer", permissions="read"),
            ]
            db.add_all(roles)
            db.flush()
            role_ids = {role.name: role.id for role in roles}

        building = db.query(Building).filter(Building.slug == "abdulrahman-building").first()
        if building is None:
            building = Building(
                name="Abdulrahman Building",
                slug="abdulrahman-building",
                description="A busy commercial building in the heart of Merkato.",
                address_text="Merkato, Addis Ababa",
                landmark="Near the central market gate",
                building_code="AB-01",
                status="active",
            )
            db.add(building)
            db.flush()

        floor = db.query(Floor).filter(
            Floor.building_id == building.id,
            Floor.floor_number == 2,
        ).first()
        if floor is None:
            floor = Floor(
                building_id=building.id,
                name="Second Floor",
                floor_number=2,
                status="active",
            )
            db.add(floor)
            db.flush()

        electronics = db.query(Category).filter(Category.slug == "electronics").first()
        if electronics is None:
            electronics = Category(name="Electronics", slug="electronics", status="active")
            db.add(electronics)

        repair = db.query(Category).filter(Category.slug == "phone-repair").first()
        if repair is None:
            repair = Category(name="Phone Repair", slug="phone-repair", status="active")
            db.add(repair)

        fashion = db.query(Category).filter(Category.slug == "womens-fashion").first()
        if fashion is None:
            fashion = Category(name="Women's Fashion", slug="womens-fashion", status="active")
            db.add(fashion)
        db.flush()

        business = db.query(Business).filter(Business.slug == "aphra-electronics").first()
        if business is None:
            business = Business(
                name="Aphra Electronics",
                slug="aphra-electronics",
                floor_id=floor.id,
                short_description="Electronics and mobile accessories",
                description="Full electronics shop with accessories, repairs, and device support.",
                status="active",
                verification_status="verified",
                phone="+251911000000",
                whatsapp="+251911000000",
                email="info@aphraelectronics.com",
                categories=[electronics, repair],
            )
            db.add(business)

        if db.query(User).filter(User.email == "admin@merkato.local").first() is None:
            db.add(
                User(
                    name="System Admin",
                    email="admin@merkato.local",
                    password_hash=hash_password("admin123"),
                    role_id=role_ids["admin"],
                    status="active",
                )
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
    print("Demo data seeded successfully.")