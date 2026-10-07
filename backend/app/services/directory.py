from app.models import Business


def serialize_business(business: Business, include_archived_categories: bool = False) -> dict:
    categories = sorted(
        [
            category
            for category in business.categories
            if include_archived_categories or category.status == "active"
        ],
        key=lambda category: category.name.casefold(),
    )
    floor = business.floor
    return {
        "id": business.id,
        "name": business.name,
        "slug": business.slug,
        "floor_id": business.floor_id,
        "short_description": business.short_description,
        "description": business.description,
        "status": business.status,
        "verification_status": business.verification_status,
        "phone": business.phone,
        "secondary_phone": business.secondary_phone,
        "whatsapp": business.whatsapp,
        "email": business.email,
        "website": business.website,
        "logo": business.logo,
        "cover_image": business.cover_image,
        "opening_hours": business.opening_hours,
        "social_links": business.social_links,
        "created_at": business.created_at,
        "updated_at": business.updated_at,
        "category_ids": [category.id for category in categories],
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "image_url": category.image_url,
                "status": category.status,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
            }
            for category in categories
        ],
        "floor": {
            "id": floor.id,
            "name": floor.name,
            "floor_number": floor.floor_number,
            "building_id": floor.building_id,
            "building_name": floor.building.name,
        },
    }