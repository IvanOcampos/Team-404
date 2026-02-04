import requests
from bs4 import BeautifulSoup
import time
import re
import sys

# --- CONFIGURACION ---
API_URL = "http://127.0.0.1:8000/products/"

HEADERS_GLOBAL = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-419,es;q=0.9",
}

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    SELENIUM_DISPONIBLE = True
except ImportError:
    SELENIUM_DISPONIBLE = False

print("-" * 60)
print(" SCRAPER FINAL - DEMO PRESENTACION")
print("-" * 60)

# ======================================================
# UTILIDADES
# ======================================================
def limpiar_precio(texto_precio):
    if not texto_precio: return None
    texto = str(texto_precio).strip().lower()
    texto = texto.replace("gs.", "").replace("gs", "").replace("pyg", "").replace("us$", "")
    texto = texto.replace(".", "").replace(",", ".").replace("\xa0", "").strip()
    try:
        match = re.search(r"(\d+(\.\d+)?)", texto)
        if match:
            valor = float(match.group(1))
            return valor if valor > 5000 else None
        return None
    except: return None

def enviar_al_backend(producto):
    try:
        if not producto['name'] or not producto['initial_price']: return
        # Filtro extra: Si el nombre sigue siendo un porcentaje, lo ignoramos
        if "%" in producto['name'] and len(producto['name']) < 5: return 
        
        response = requests.post(API_URL, json=producto)
        if response.status_code == 200:
            print(f"[OK] {producto['store']}: {producto['name'][:40]}...")
    except: pass

# ======================================================
# 1. TIENDAS RAPIDAS (Requests)
# ======================================================
def scraper_fast(nombre, url, sel_card, sel_name, sel_price, sel_img):
    print(f"[INFO] Procesando {nombre}...")
    try:
        res = requests.get(url, headers=HEADERS_GLOBAL, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select(sel_card)
        
        count = 0
        for item in items[:15]:
            try:
                name = item.select_one(sel_name).text.strip()
                link = url
                a_tag = item.select_one(sel_name) if item.select_one(sel_name).name == 'a' else item.find("a")
                if a_tag: link = a_tag['href']

                price = limpiar_precio(item.select_one(sel_price).text)
                
                img_tag = item.select_one(sel_img)
                img = img_tag['src'] if img_tag else None

                if price:
                    enviar_al_backend({"name": name, "url": link, "initial_price": price, "store": nombre, "image_url": img})
                    count += 1
            except: continue
        print(f"[INFO] {nombre} finalizado: {count} items.")
    except Exception as e: print(f"[ERROR] {nombre}: {e}")

# ======================================================
# 2. TIENDAS SELENIUM (TiendaMovil & TopTechnology)
# ======================================================
def scraper_selenium(driver, tiendas):
    for tienda in tiendas:
        nombre = tienda['nombre']
        url = tienda['url']
        print(f"[INFO] Navegando en {nombre}...")

        try:
            driver.get(url)
            time.sleep(5) 
            driver.execute_script("window.scrollTo(0, 800);")
            time.sleep(2)

            posibles_tarjetas = ["article.product-miniature", "div.product-grid-item"]
            
            items = []
            for sel in posibles_tarjetas:
                items = driver.find_elements(By.CSS_SELECTOR, sel)
                if len(items) > 0: break 

            count = 0
            for item in items[:15]:
                try:
                    # 1. PRECIO
                    texto = item.text
                    precio = None
                    for linea in texto.split('\n'):
                        p = limpiar_precio(linea)
                        if p: 
                            precio = p
                            break
                    if not precio: continue

                    # 2. NOMBRE (CORRECCION PARA TIENDAMOVIL)
                    titulo = "Producto sin nombre"
                    link = url
                    
                    try:
                        if nombre == "TiendaMovil":
                            # En TiendaMovil buscamos especificamente el H3 o la clase product-title
                            # para evitar el badge de "-17%"
                            titulo_elem = item.find_element(By.CSS_SELECTOR, "h3.product-title, .product-title a")
                            titulo = titulo_elem.text.strip()
                            link = titulo_elem.get_attribute("href") if titulo_elem.tag_name == 'a' else item.find_element(By.TAG_NAME, "a").get_attribute("href")
                        else:
                            # Logica estandar para TopTechnology
                            tag_a = item.find_element(By.TAG_NAME, "a")
                            titulo = tag_a.text or item.text.split('\n')[0]
                            link = tag_a.get_attribute("href")
                    except:
                        # Fallback por si falla el selector especifico
                        try:
                            # Buscamos cualquier enlace que tenga texto largo (mas de 5 letras)
                            enlaces = item.find_elements(By.TAG_NAME, "a")
                            for a in enlaces:
                                if len(a.text) > 5:
                                    titulo = a.text
                                    link = a.get_attribute("href")
                                    break
                        except: pass

                    # 3. IMAGEN
                    img = None
                    try:
                        img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                    except: pass

                    enviar_al_backend({"name": titulo, "url": link, "initial_price": precio, "store": nombre, "image_url": img})
                    count += 1
                except: continue
            
            print(f"[INFO] {nombre} finalizado: {count} items.")

        except Exception as e:
            print(f"[ERROR] {e}")

# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    
    # 1. NISSEI & CELLSHOP
    scraper_fast("Nissei", "https://nissei.com/py/electronica/celulares-tabletas/celulares-accesorios/telefonos-inteligentes", "li.product-item", "a.product-item-link", "[data-price-amount]", "img.product-image-photo")
    scraper_fast("CellShop", "https://cellshop.com.py/telefonia", ".product-item-info", ".product-item-link", ".price", "img")

    # 2. SELENIUM (TiendaMovil + TopTechnology)
    if SELENIUM_DISPONIBLE:
        print("[INFO] Iniciando Selenium (Oculto)...")
        options = Options()
        options.add_argument("--headless=new") 
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--log-level=3")
        
        driver = webdriver.Chrome(options=options)
        
        tiendas_seguras = [
            {"nombre": "TiendaMovil", "url": "https://tiendamovil.com.py/shop/"},
            {"nombre": "TopTechnology", "url": "https://toptechnology.com.py/comprar/celulares-smartphone/"}
        ]

        try:
            scraper_selenium(driver, tiendas_seguras)
        finally:
            driver.quit()
            print("[INFO] Proceso Terminado.")
    else:
        print("[WARN] Selenium no instalado.")