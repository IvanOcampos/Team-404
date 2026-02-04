from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, unique=True)
    image_url = Column(String, nullable=True)
    # p ara saber si vino de la 'web' o del 'bot'
    source = Column(String, default="web") 
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("Price", back_populates="product")

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    currency = Column(String, default="Gs")
    store = Column(String)
    captured_at = Column(DateTime, default=datetime.utcnow)
    
    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="prices")

class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    keyword = Column(String)
    target_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)