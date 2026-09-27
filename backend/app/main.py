from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.config import settings
from app.models import AdminUser, Building, Category, Room, Business


def seed_database(db: Session):
    existing_admin = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
    if not existing_admin:
        db.add(
            AdminUser(
                username=settings.ADMIN_USERNAME,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin",
            )
        )

    if db.query(Building).count() > 0:
        return

    building_1 = Building(
        name="Building 1",
        description="Main commercial building with electronics and fashion shops.",
        image_url="https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1200&q=80",
        sort_order=1,
        is_published=True,
    )
    building_2 = Building(
        name="Building 2",
        description="Food and retail hub for local businesses.",
        image_url="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
        sort_order=2,
        is_published=True,
    )

    electronics = Category(
        name="Electronics",
        description="Phones, repairs, and tech goods.",
        image_url="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
        sort_order=1,
        is_published=True,
    )
    fashion = Category(
        name="Clothing",
        description="Fashion and accessories.",
        image_url="https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=80",
        sort_order=2,
        is_published=True,
    )
    food = Category(
        name="Food",
        description="Dining and quick bites.",
        image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=1200&q=80",
        sort_order=1,
        is_published=True,
    )

    room_101 = Room(
        room_number="101",
        name="ABC Electronics",
        description="Repair and sales shop for smartphones, gadgets, and accessories.",
        image_url="https://images.unsplash.com/photo-1580910051074-3e8d6a1f95e6?auto=format&fit=crop&w=1200&q=80",
        sort_order=1,
        is_published=True,
    )
    room_204 = Room(
        room_number="204",
        name="XYZ Fashion",
        description="Women and men clothing boutique.",
        image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80",
        sort_order=2,
        is_published=True,
    )
    room_12 = Room(
        room_number="12",
        name="ABC Restaurant",
        description="Family restaurant and takeaway kitchen.",
        image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=1200&q=80",
        sort_order=1,
        is_published=True,
    )

    building_1.categories = [electronics, fashion]
    building_2.categories = [food]
    electronics.rooms = [room_101]
    fashion.rooms = [room_204]
    food.rooms = [room_12]

    room_101.business = Business(
        business_name="ABC Electronics",
        description="Trusted repair and upgrade specialists for phones, accessories, and laptop support.",
        phone="+12345678901",
        alternative_phone="+12345678902",
        telegram="@abcelectronics",
        whatsapp="+12345678901",
        facebook="https://facebook.com/abcelectronics",
        instagram="https://instagram.com/abcelectronics",
        website="https://example.com/abcelectronics",
        opening_hours="Mon-Sat: 9:00 - 19:00",
        services="Phone repair, laptop repair, accessories, custom setup",
        products="Smartphone screens, chargers, headphones, cases",
        notes="Same-day repair service available.",
        image_url="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
        gallery_images=[
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80",
        ],
        is_published=True,
    )

    room_204.business = Business(
        business_name="XYZ Fashion",
        description="Contemporary styling for everyday essentials and special occasions.",
        phone="+12345678903",
        telegram="@xyzfashion",
        instagram="https://instagram.com/xyzfashion",
        website="https://example.com/xyzfashion",
        opening_hours="Mon-Sun: 10:00 - 20:00",
        services="Tailoring, personal styling, accessories",
        products="Dresses, jackets, scarves, handbags",
        notes="Seasonal collections available.",
        image_url="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1200&q=80",
        gallery_images=[
            "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1200&q=80",
        ],
        is_published=True,
    )

    room_12.business = Business(
        business_name="ABC Restaurant",
        description="Casual dining and takeaway favorites for locals and visitors.",
        phone="+12345678904",
        whatsapp="+12345678904",
        facebook="https://facebook.com/abcrestaurant",
        website="https://example.com/abcrestaurant",
        opening_hours="Daily: 8:00 - 22:00",
        services="Dining, takeaway, catering",
        products="Rice bowls, grilled meals, desserts",
        notes="Vegetarian options available.",
        image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=1200&q=80",
        gallery_images=[
            "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80",
        ],
        is_published=True,
    )

    db.add_all([building_1, building_2])
    db.commit()
