from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Esquemas internos para PRECIOS
class PriceBase(BaseModel):
    amount: float
    store: str

class PriceResponse(PriceBase):
    id: int
    captured_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para PRODUCTOS 

# Lo que recibimos del Scraper (Input)
class ProductCreate(BaseModel):
    name: str
    url: str
    image_url: Optional[str] = None
    initial_price: float  # Dato crucial para crear el primer registro
    store: str            # Tienda donde se encontró

# Lo que enviamos al Frontend (Output)
class ProductResponse(BaseModel):
    id: int
    name: str
    url: str
    image_url: Optional[str] = None
    created_at: datetime
    # El frontend recibirá una lista con todo el historial de precios
    prices: List[PriceResponse] = []

    class Config:
        from_attributes = True