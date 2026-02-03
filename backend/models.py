from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
# Importación directa (sin el punto si están en la misma carpeta)
from database import Base 

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    store = Column(String)
    url = Column(String, unique=True)
    image_url = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)