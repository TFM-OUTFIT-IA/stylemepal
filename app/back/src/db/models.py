from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .database import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    image_path = Column(String)
    name = Column(String)
    clean = Column(Boolean, default=True)
    
    # ML Extracted Metadata
    category = Column(String, index=True)
    style = Column(String)
    weather = Column(String)
    gender = Column(String)
    
    # 512-D FashionCLIP Vector
    # embedding = Column(Vector(512))

    # 128-D RGCN Comaptibility Vector
    compat_embedding = Column(Vector(128))

class OutfitDB(Base):
    __tablename__ = "outfits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # Filters used when generating this outfit
    style = Column(String)
    weather = Column(String)
    gender = Column(String)

    items_snapshot = Column(JSON)

    worn_at = Column(DateTime(timezone=True), server_default=func.now())