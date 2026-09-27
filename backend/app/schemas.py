from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


class AdminUserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    sort_order: int = 0
    is_published: bool = True

    @field_validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Building name cannot be empty')
        return v.strip()


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BuildingBase):
    pass


class BuildingResponse(BuildingBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    sort_order: int = 0
    is_published: bool = True

    @field_validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip()


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    building_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    sort_order: int = 0
    is_published: bool = True

    @field_validator('room_number', 'name')
    def fields_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    category_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BusinessBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    phone: Optional[str] = Field(None, max_length=40)
    alternative_phone: Optional[str] = Field(None, max_length=40)
    telegram: Optional[str] = Field(None, max_length=120)
    whatsapp: Optional[str] = Field(None, max_length=120)
    facebook: Optional[str] = Field(None, max_length=200)
    instagram: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=300)
    opening_hours: Optional[str] = Field(None, max_length=500)
    services: Optional[str] = Field(None, max_length=2000)
    products: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    is_published: bool = True

    @field_validator('business_name')
    def business_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Business name cannot be empty')
        return v.strip()


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BusinessBase):
    pass


class BusinessResponse(BusinessBase):
    id: int
    room_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    url: str
    filename: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
