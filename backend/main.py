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
@app.get("/")
def read_root():
    return {"message": "API OfferHunt v2 con Historial de Precios"}

# Endpoint Inteligente: Crea o Actualiza
@app.post("/products/", response_model=schemas.ProductResponse)
def create_or_update_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    # 1. Buscar si el producto ya existe en nuestra DB (por URL)
    existing_product = db.query(models.Product).filter(models.Product.url == product_in.url).first()

    if existing_product:
        # CASO A: El producto ya existe. Solo registramos el nuevo precio.
        new_price = models.Price(
            amount=product_in.initial_price,
            store=product_in.store,
            product_id=existing_product.id
        )
        db.add(new_price)
        db.commit()
        db.refresh(existing_product) # Recargamos para devolver el producto con el nuevo historial
        return existing_product
    
    else:
        # CASO B: Es un producto nuevo. Creamos Producto + Primer Precio.
        # Paso 1: Crear Producto
        new_product = models.Product(
            name=product_in.name,
            url=product_in.url,
            image_url=product_in.image_url
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product) # Obtenemos el ID generado
        
        # Paso 2: Crear el primer precio asociado
        new_price = models.Price(
            amount=product_in.initial_price,
            store=product_in.store,
            product_id=new_product.id
        )
        db.add(new_price)
        db.commit()
        
        db.refresh(new_product)
        return new_product

@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # SQLAlchemy traerá automáticamente los precios gracias a la 'relationship'
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products