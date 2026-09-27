"""Seed database with sample data."""
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.config import settings
from app.models import AdminUser, Building, Category, Room, Business


def seed_database(db: Session):
    """Seed the database with initial admin user and sample directory data."""
    # Create admin user if it doesn't exist
    existing_admin = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
    if not existing_admin:
        admin = AdminUser(
            username=settings.ADMIN_USERNAME,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            role="admin",
        )
        db.add(admin)
        db.commit()

    # Only seed if no buildings exist
    if db.query(Building).count() > 0:
        return

    # Create buildings
    building_1 = Building(
        name="Building 1",
        description="Main commercial building with electronics and fashion shops.",
        image_url="https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=400&h=300&fit=crop",
        sort_order=1,
        is_published=True,
    )
    building_2 = Building(
        name="Building 2",
        description="Food and retail hub for local businesses.",
        image_url="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400&h=300&fit=crop",
        sort_order=2,
        is_published=True,
    )

    # Create categories
    electronics = Category(
        name="Electronics",
        description="Phones, repairs, and tech goods.",
        image_url="https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop",
        sort_order=1,
        is_published=True,
    )
    fashion = Category(
        name="Clothing",
        description="Fashion and accessories.",
        image_url="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=300&fit=crop",
        sort_order=2,
        is_published=True,
    )
    food = Category(
        name="Food",
        description="Dining and quick bites.",
        image_url="https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400&h=300&fit=crop",
        sort_order=1,
        is_published=True,
    )

    # Create rooms
    room_101 = Room(
        room_number="101",
        name="ABC Electronics",
        description="Repair and sales shop for smartphones, gadgets, and accessories.",
        image_url="https://images.unsplash.com/photo-1580910051074-3e8d6a1f95e6?w=400&h=300&fit=crop",
        sort_order=1,
        is_published=True,
    )
    room_204 = Room(
        room_number="204",
        name="XYZ Fashion",
        description="Women and men clothing boutique.",
        image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=400&h=300&fit=crop",
        sort_order=2,
        is_published=True,
    )
    room_12 = Room(
        room_number="12",
        name="ABC Restaurant",
        description="Family restaurant and takeaway kitchen.",
        image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
        sort_order=1,
        is_published=True,
    )

    # Assign categories to buildings
    building_1.categories = [electronics, fashion]
    building_2.categories = [food]

    # Assign rooms to categories
    electronics.rooms = [room_101]
    fashion.rooms = [room_204]
    food.rooms = [room_12]

    # Create business records
    business_1 = Business(
        business_name="ABC Electronics",
        description="Trusted repair and upgrade specialists for phones, accessories, and laptop support. We offer same-day service for most repairs.",
        phone="+1-234-567-8901",
        alternative_phone="+1-234-567-8902",
        telegram="@abcelectronics",
        whatsapp="+1-234-567-8901",
        facebook="https://facebook.com/abcelectronics",
        instagram="https://instagram.com/abcelectronics",
        website="https://example.com/abcelectronics",
        opening_hours="Mon-Sat: 9:00 AM - 7:00 PM | Sun: 10:00 AM - 5:00 PM",
        services="Phone repair, Laptop repair, Device upgrades, Screen replacement, Battery replacement, Water damage repair",
        products="Smartphone screens, Chargers, Headphones, Phone cases, Screen protectors, Charging cables",
        notes="Same-day repair service available. Professional technicians with 10+ years of experience.",
        image_url="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop",
        gallery_images=[
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop",
        ],
        is_published=True,
    )

    business_2 = Business(
        business_name="XYZ Fashion",
        description="Contemporary styling for everyday essentials and special occasions. Featuring local and international designers.",
        phone="+1-234-567-8903",
        telegram="@xyzfashion",
        instagram="https://instagram.com/xyzfashion",
        website="https://example.com/xyzfashion",
        opening_hours="Mon-Sun: 10:00 AM - 8:00 PM",
        services="Tailoring, Personal styling, Alterations, Accessories consultation, Seasonal wardrobe planning",
        products="Dresses, Jackets, Scarves, Handbags, Shoes, Accessories, Jewelry",
        notes="Seasonal collections available. Visit us for new arrivals every month.",
        image_url="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&h=300&fit=crop",
        gallery_images=[
            "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=400&h=300&fit=crop",
            "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=300&fit=crop",
        ],
        is_published=True,
    )

    business_3 = Business(
        business_name="ABC Restaurant",
        description="Casual dining and takeaway favorites for locals and visitors. Fresh ingredients and authentic recipes.",
        phone="+1-234-567-8904",
        whatsapp="+1-234-567-8904",
        facebook="https://facebook.com/abcrestaurant",
        website="https://example.com/abcrestaurant",
        opening_hours="Daily: 8:00 AM - 10:00 PM",
        services="Dining in, Takeaway, Catering, Private events, Meal prep delivery",
        products="Rice bowls, Grilled meats, Pasta dishes, Salads, Desserts, Beverages",
        notes="Vegetarian and vegan options available. Order online for faster service.",
        image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
        gallery_images=[
            "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&h=300&fit=crop",
            "https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=300&fit=crop",
        ],
        is_published=True,
    )

    # Assign businesses to rooms
    room_101.business = business_1
    room_204.business = business_2
    room_12.business = business_3

    # Save all
    db.add_all([building_1, building_2])
    db.commit()
