from typing import Optional
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class BuildingCreate(BaseModel):
    name: str
    description: str = ""
    image_url: str = ""
    sort_order: int = 0
    is_published: bool = True

class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_published: Optional[bool] = None

class CategoryCreate(BaseModel):
    name: str
    description: str = ""
    image_url: str = ""
    sort_order: int = 0
    is_published: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_published: Optional[bool] = None

class RoomCreate(BaseModel):
    room_number: str
    name: str
    description: str = ""
    image_url: str = ""
    sort_order: int = 0
    is_published: bool = True

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_published: Optional[bool] = None

class BusinessCreate(BaseModel):
    business_name: str
    description: str = ""
    phone: str = ""
    alternative_phone: str = ""
    telegram: str = ""
    whatsapp: str = ""
    facebook: str = ""
    instagram: str = ""
    website: str = ""
    opening_hours: str = ""
    services: str = ""
    products: str = ""
    notes: str = ""
    image_url: str = ""
    gallery_images: list = []
    is_published: bool = True

class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
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
    gallery_images: Optional[list] = None
    is_published: Optional[bool] = None

class UploadResponse(BaseModel):
    url: str
    filename: str
