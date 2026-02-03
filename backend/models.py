from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, unique=True) # URL principal para identificarlo
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación: Un producto tiene MUCHOS precios
    prices = relationship("Price", back_populates="product")

class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    currency = Column(String, default="Gs") # Moneda por defecto: Guaraníes
    store = Column(String) # Ej: Amazon, eBay
    captured_at = Column(DateTime, default=datetime.utcnow)
    
    # Llave foránea: Este precio pertenece a un Producto específico
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Relación inversa
    product = relationship("Product", back_populates="prices")