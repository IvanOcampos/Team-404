from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import models
import schemas
from database import SessionLocal, engine
from scraper_dinamico import buscar_productos_en_web 

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI() 

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia: Abre y cierra la DB por cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint Raíz
@app.get("/")
def read_root():
    return {"message": "API OfferHunt v2 con Búsqueda en Vivo"}

# devuelve una Lista de Productos y marca el origen como "web"
@app.post("/search-live/", response_model=List[schemas.ProductResponse])
def search_live(keyword: str, db: Session = Depends(get_db)):
 
    print(f"📡 Recibida petición de búsqueda en vivo (WEB): {keyword}")
    try:
        # Ejecutamos el scraper enviando origen="web"
        ids_encontrados = buscar_productos_en_web(keyword, origen="web")
        
        # Si no se encuentra nada, devolvemos lista vacía
        if not ids_encontrados:
            return []

        # consultar en la DB solo esos productos específicos
        productos = db.query(models.Product)\
            .filter(models.Product.id.in_(ids_encontrados))\
            .all()
            
        return productos

    except Exception as e:
        print(f"Error en endpoint search-live: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Crear o actualizar producto.
@app.post("/products/", response_model=schemas.ProductResponse)
def create_or_update_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    # Buscar si el producto ya existe en nuestra DB (por URL)
    existing_product = db.query(models.Product).filter(models.Product.url == product_in.url).first()

    if existing_product:
        # Si el producto ya existe solo registramos el nuevo precio.
        new_price = models.Price(
            amount=product_in.initial_price,
            store=product_in.store,
            product_id=existing_product.id
        )
        db.add(new_price)
        db.commit()
        db.refresh(existing_product)
        return existing_product
    
    else:
        # si es un producto nuevo. Creamos Producto + Primer Precio.
        new_product = models.Product(
            name=product_in.name,
            url=product_in.url,
            image_url=product_in.image_url,
            source="web" # por defecto se asume como web si ingresa por este endpoint
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        new_price = models.Price(
            amount=product_in.initial_price,
            store=product_in.store,
            product_id=new_product.id
        )
        db.add(new_price)
        db.commit()
        
        db.refresh(new_product)
        return new_product

# Filtra para mostrar SOLO lo que tiene source="web"
@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(search: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    
    # Filtro para mostrar solo los productos que vienen de la web.
    query = query.filter(models.Product.source == "web")

    # Si el usuario envió un término de búsqueda, se filtra por nombre también
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    
    # Ordenar por ID descendente.
    products = query.order_by(models.Product.id.desc()).offset(skip).limit(limit).all()
    
    return products