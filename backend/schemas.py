from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Esquema para precios.
class PriceBase(BaseModel):
    amount: float
    store: str

class PriceCreate(PriceBase):
    product_id: int

class Price(PriceBase):
    id: int
    captured_at: datetime
    
    class Config:
        from_attributes = True 

# Esquema para productos.
class ProductBase(BaseModel):
    name: str
    url: str
    image_url: Optional[str] = None

# Lo que se recibe al crear un producto (desde el Scraper)
class ProductCreate(ProductBase):
    initial_price: float
    store: str

# Lo que se envia al Frontend.
class ProductResponse(ProductBase):
    id: int
    prices: List[Price] = []

    class Config:
        from_attributes = True