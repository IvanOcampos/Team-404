import requests
import random

API_URL = "http://127.0.0.1:8000/products/"

# Datos de prueba
nombres = ["iPhone 15", "Samsung S24", "MacBook Air", "Sony Headphones", "Logitech Mouse", "Monitor Dell", "Teclado Mecánico"]
tiendas = ["Amazon", "eBay", "BestBuy", "Walmart"]

print("Sembrando base de datos...")

for i in range(20):
    producto = {
        "name": f"{random.choice(nombres)} - Modelo {i}",
        "url": f"https://tienda.com/prod-{i}",
        "image_url": "https://via.placeholder.com/150",
        "initial_price": round(random.uniform(50.0, 1500.0), 2),
        "store": random.choice(tiendas)
    }
    
    try:
        response = requests.post(API_URL, json=producto)
        if response.status_code == 200:
            print(f"Guardado: {producto['name']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error de conexión: {e}")

print("¡Proceso terminado!")