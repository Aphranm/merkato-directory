from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="admin")
    created_at = Column(DateTime, default=datetime.utcnow)

class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    description = Column(Text, default="")
    image_url = Column(String(500), default="")
    sort_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    categories = relationship("Category", back_populates="building", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), index=True)
    name = Column(String(255), index=True)
    description = Column(Text, default="")
    image_url = Column(String(500), default="")
    sort_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    building = relationship("Building", back_populates="categories")
    rooms = relationship("Room", back_populates="category", cascade="all, delete-orphan")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)
    room_number = Column(String(50), index=True)
    name = Column(String(255), index=True)
    description = Column(Text, default="")
    image_url = Column(String(500), default="")
    sort_order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("Category", back_populates="rooms")
    business = relationship("Business", back_populates="room", cascade="all, delete-orphan", uselist=False)

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), unique=True, index=True)
    business_name = Column(String(255), index=True)
    description = Column(Text, default="")
    phone = Column(String(50), default="")
    alternative_phone = Column(String(50), default="")
    telegram = Column(String(100), default="")
    whatsapp = Column(String(50), default="")
    facebook = Column(String(100), default="")
    instagram = Column(String(100), default="")
    website = Column(String(500), default="")
    opening_hours = Column(String(255), default="")
    services = Column(Text, default="")
    products = Column(Text, default="")
    notes = Column(Text, default="")
    image_url = Column(String(500), default="")
    gallery_images = Column(JSON, default=list)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    room = relationship("Room", back_populates="business")
