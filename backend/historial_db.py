from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import random
from datetime import datetime, timedelta

# Aseguramos que las tablas existan
models.Base.metadata.create_all(bind=engine)

def crear_historial_ficticio():
    db = SessionLocal()
    try:
        productos = db.query(models.Product).all()
        
        if not productos:
            print(" No hay productos en la base de datos. Primero busca algo en la web.")
            return

        print(f"🔄 Generando historia para {len(productos)} productos...")

        cambios_totales = 0

        for p in productos:
            # Obtenemos el precio actual (el último registrado)
            if not p.prices: continue
            precio_base = p.prices[-1].amount
            store = p.prices[-1].store

            # Vamos a inventar 4 días hacia atrás
            for dias_atras in range(1, 5):
                # Fecha pasada
                fecha_falsa = datetime.now() - timedelta(days=dias_atras)
                
                # Variación de precio (entre -15% y +15%)
                variacion = random.uniform(0.85, 1.15)
                precio_falso = int(precio_base * variacion)

                # Crear el precio antiguo
                nuevo_precio_historia = models.Price(
                    amount=precio_falso,
                    store=store,
                    product_id=p.id,
                    captured_at=fecha_falsa
                )
                db.add(nuevo_precio_historia)
                cambios_totales += 1
        
        db.commit()
        print(f" Se agregaron {cambios_totales} precios históricos falsos.")
        print(" Ahora actualiza tu página web y mira los gráficos.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    crear_historial_ficticio()