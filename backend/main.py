from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000", # Puerto común de React
    "http://localhost:5173", # Puerto común de Vite/Vue
    "*"                      # Permite todo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # O usa ["*"] para permitir a cualquiera
    allow_credentials=True,
    allow_methods=["*"],   # Permitir GET, POST, PUT, DELETE
    allow_headers=["*"],
)

# Dependencia: Abre y cierra la DB por cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "API de OfferHunt funcionando"}

# Endpoint para CREAR productos (Usado por el Scraper)
@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Verificamos si ya existe la URL para no duplicar
    db_product = db.query(models.Product).filter(models.Product.url == product.url).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Este producto ya existe")
    
    # Convertimos el esquema de Pydantic a Modelo de SQLAlchemy
    new_product = models.Product(**product.dict())
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Endpoint para LEER productos (Usado por el Frontend)
@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products