import requests
from bs4 import BeautifulSoup
import time
import random

# URL DE TU BACKEND (Asegúrate de que uvicorn esté corriendo)
API_URL = "http://127.0.0.1:8000/products/"

# Configuración de Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_DISPONIBLE = True
except ImportError:
    SELENIUM_DISPONIBLE = False
    print("⚠️ Selenium no instalado. Ejecuta: pip install selenium")

print("\n" + "="*70)
print("🚀 SCRAPER CONECTADO AL BACKEND - TEAM 404".center(70))
print("="*70 + "\n")

# ======================================================
# 1. FUNCIÓN PARA LIMPIAR PRECIOS
# ======================================================
def limpiar_precio(texto_precio):
    """Convierte 'Gs. 1.500.000' a float 1500000.0"""
    if not texto_precio: return None
    texto = texto_precio.strip()
    if "Gs" not in texto and "PYG" not in texto: return None # Validación básica

    try:
        limpio = (texto.replace("Gs.", "")
                       .replace("Gs", "")
                       .replace("PYG", "")
                       .replace(".", "")
                       .replace(",", "")
                       .replace("\xa0", "")
                       .strip())
        return float(limpio)
    except:
        return None

# ======================================================
# 2. FUNCIÓN PARA ENVIAR AL BACKEND (¡NUEVO!)
# ======================================================
def enviar_al_backend(producto):
    """Envía un solo producto a tu API FastAPI"""
    # Mapeo de datos: Lo que tiene el scraper -> Lo que pide el Backend (schemas.py)
    payload = {
        "name": producto['titulo'],
        "url": producto['link'],
        "initial_price": producto['precio_numero'],
        "store": producto['tienda'],
        "image_url": producto.get('imagen', None) # Ahora enviamos foto
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Guardado DB: {producto['titulo'][:30]}...")
        else:
            # Si ya existe (a veces devolvemos el objeto, a veces error 400 segun logica)
            # En tu backend actual, si existe, devuelve el producto actualizado (200 OK)
            print(f"⚠️ Respuesta API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión con API: {e}")

# ======================================================
# 3. SCRAPER NISSEI (Mejorado con Imágenes)
# ======================================================
def scraper_nissei():
    print("🔍 Scrapeando Nissei...")
    
    # URL de ejemplo (Celulares)
    url = "https://nissei.com/py/electronica/celulares-tabletas/celulares-accesorios/telefonos-inteligentes"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://nissei.com/py/",
    }

    try:
        time.sleep(random.uniform(1, 2))
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"⚠️ Nissei bloqueó la conexión ({response.status_code})")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("li", class_="product-item")
        
        print(f"   Encontrados {len(items)} items. Procesando...")

        for item in items:
            try:
                # Datos básicos
                titulo_tag = item.find("a", class_="product-item-link")
                if not titulo_tag: continue
                
                titulo = titulo_tag.text.strip()
                link = titulo_tag.get("href", "")

                # --- EXTRACCIÓN DE IMAGEN (NUEVO) ---
                img_tag = item.find("img", class_="product-image-photo")
                img_url = img_tag.get("src") if img_tag else None
                # ------------------------------------

                # Extracción de Precio (Simplificada para el ejemplo)
                precio_final = 0
                price_box = item.find("span", attrs={"data-price-amount": True})
                if price_box:
                    precio_final = float(price_box.get("data-price-amount", 0))
                
                # Solo guardar si hay precio y título
                if precio_final > 0:
                    producto = {
                        "tienda": "Nissei",
                        "titulo": titulo,
                        "precio_numero": precio_final,
                        "link": link,
                        "imagen": img_url
                    }
                    # ENVIAR AL INSTANTE AL BACKEND
                    enviar_al_backend(producto)

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Error Nissei: {e}")

# ======================================================
# 4. SCRAPER SHOPPING CHINA (Optimizado)
# ======================================================
def scraper_shopping_china():
    if not SELENIUM_DISPONIBLE: return

    print("\n🔍 Scrapeando Shopping China...")
    url = "https://www.shoppingchina.com.py/electronicos" # URL Directa

    options = Options()
    # options.add_argument("--headless") # Descomenta para que no abra la ventana
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Scroll rápido para cargar lazy-load images
        driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(3)

        # Capturamos las TARJETAS de la lista (Más rápido que entrar uno por uno)
        # Nota: Los selectores pueden cambiar, esto es un ejemplo genérico de estructura
        productos_dom = driver.find_elements(By.CSS_SELECTOR, "div.product-item") # Ajustar selector si falla
        
        # Si no encuentra por clase genérica, buscamos enlaces
        if not productos_dom:
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/producto/')]")
            # Limitamos a 5 para prueba rápida, quita el [:5] para producción
            links_unicos = list(dict.fromkeys([l.get_attribute("href") for l in links]))[:10] 
            
            print(f"   Procesando {len(links_unicos)} productos detallados...")

            for link in links_unicos:
                try:
                    driver.get(link)
                    time.sleep(1)

                    # Título
                    try:
                        titulo = driver.find_element(By.TAG_NAME, "h1").text.strip()
                    except: continue

                    # Precio
                    try:
                        precio_txt = driver.find_element(By.CLASS_NAME, "sc-text-danger").text
                        precio_num = limpiar_precio(precio_txt)
                    except: continue

                    # --- IMAGEN (NUEVO) ---
                    try:
                        # Busca la imagen principal del slider o contenedor
                        img_elem = driver.find_element(By.CSS_SELECTOR, "div.product-image-container img")
                        img_url = img_elem.get_attribute("src")
                    except: 
                        img_url = None
                    # ----------------------

                    if precio_num:
                        prod = {
                            "tienda": "Shopping China",
                            "titulo": titulo,
                            "precio_numero": precio_num,
                            "link": link,
                            "imagen": img_url
                        }
                        enviar_al_backend(prod)

                except Exception:
                    continue
    except Exception as e:
        print(f"❌ Error Shopping China: {e}")
    finally:
        driver.quit()

# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    print("⏳ Iniciando recolección de datos...")
    
    # 1. Nissei (Rápido)
    scraper_nissei()
    
    # 2. Shopping China (Lento pero seguro)
    scraper_shopping_china()
    
    print("\n✨ Proceso finalizado. Revisa tu Frontend.")