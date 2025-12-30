from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
from app.db.base_class import BaseColumn
from sqlalchemy import Column, Integer, String, ForeignKey, Text,TIMESTAMP, Boolean,DateTime, Enum,Float,JSON
from sqlalchemy.sql import func
from datetime import datetime

class ProductRecord(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)          # Actual product title from site
    price = Column(Float)
    rating = Column(String)
    platform = Column(String)      # Amazon or Flipkart
    image_url = Column(String)
    final_attributes = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    