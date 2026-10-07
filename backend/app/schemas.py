from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class RoleCreate(BaseModel):
    name: str
    permissions: str = ""


class RoleOut(RoleCreate):
    id: int


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role_id: int


class UserLogin(BaseModel):
    email: str
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class EmailChange(BaseModel):
    current_password: str
    new_email: str = Field(min_length=6, max_length=254)

    @field_validator("new_email")
    @classmethod
    def validate_email_address(cls, value: str) -> str:
        value = value.strip()
        local, separator, domain = value.rpartition("@")
        labels = domain.split(".")
        valid_local = re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+", local)
        valid_domain = all(
            re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
            for label in labels
        )
        if (
            not separator
            or not valid_local
            or local.startswith(".")
            or local.endswith(".")
            or ".." in local
            or len(local) > 64
            or len(labels) < 2
            or not valid_domain
        ):
            raise ValueError("Enter a valid email address")
        return value


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    status: str = "active"
    role_id: int
    role: Optional[str] = None
    created_at: datetime


class BuildingCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    address_text: Optional[str] = None
    landmark: Optional[str] = None
    building_code: Optional[str] = None
    status: str = "active"


class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    address_text: Optional[str] = None
    landmark: Optional[str] = None
    building_code: Optional[str] = None
    status: Optional[str] = None


class BuildingOut(BuildingCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class FloorCreate(BaseModel):
    building_id: int
    name: str
    floor_number: int
    description: Optional[str] = None
    status: str = "active"


class FloorUpdate(BaseModel):
    building_id: Optional[int] = None
    name: Optional[str] = None
    floor_number: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


class FloorOut(FloorCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    status: str = "active"


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None


class CategoryOut(CategoryCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class BusinessCreate(BaseModel):
    name: str
    slug: str
    floor_id: int
    short_description: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    verification_status: str = "unverified"
    phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    cover_image: Optional[str] = None
    opening_hours: Optional[str] = None
    social_links: Optional[str] = None
    category_ids: list[int] = Field(default_factory=list)


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    floor_id: Optional[int] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    verification_status: Optional[str] = None
    phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo: Optional[str] = None
    cover_image: Optional[str] = None
    opening_hours: Optional[str] = None
    social_links: Optional[str] = None
    category_ids: Optional[list[int]] = None


class FloorSummaryOut(BaseModel):
    id: int
    name: str
    floor_number: int
    building_id: int
    building_name: str


class BusinessOut(BusinessCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryOut] = Field(default_factory=list)
    floor: FloorSummaryOut


class ImageOut(BaseModel):
    id: int
    business_id: Optional[int] = None
    file_url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_primary: bool = False
    created_at: datetime


class ReportUpdate(BaseModel):
    status: Literal["pending", "resolved", "dismissed"]


class VerificationUpdate(BaseModel):
    status: Literal["pending", "verified", "rejected"]
    notes: Optional[str] = None


class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1)
    building: Optional[str] = None
    category: Optional[str] = None
    page: int = 1
    limit: int = 20
