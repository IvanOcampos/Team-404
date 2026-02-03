from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esto es lo que recibes del Scraper (Input)
class ProductCreate(BaseModel):
    name: str
    price: float
    store: str
    url: str
    image_url: Optional[str] = None

# Esto es lo que devuelves al Frontend (Output)
# Incluye el ID y la fecha, que los genera la DB, no el usuario.
class ProductResponse(ProductCreate):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True # Antes se llamaba orm_mode = True