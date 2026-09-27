from typing import List, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


class BuildingBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_published: bool = True


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BuildingBase):
    pass


class CategoryBase(BaseModel):
    building_id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_published: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class RoomBase(BaseModel):
    category_id: int
    room_number: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: int = 0
    is_published: bool = True


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class BusinessBase(BaseModel):
    room_id: int
    business_name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    alternative_phone: Optional[str] = None
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    website: Optional[str] = None
    opening_hours: Optional[str] = None
    services: Optional[str] = None
    products: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    is_published: bool = True


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BusinessBase):
    pass


class UploadResponse(BaseModel):
    url: str
    filename: str
