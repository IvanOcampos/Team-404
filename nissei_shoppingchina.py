"""
WEB SCRAPER - Comparador de Precios
Nissei: requests + BeautifulSoup
Shopping China: Selenium con webdriver-manager
"""

import requests
from bs4 import BeautifulSoup
import time
import random

# Para Shopping China necesitamos Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_DISPONIBLE = True
except ImportError:
    SELENIUM_DISPONIBLE = False
    print("⚠️ Selenium o webdriver-manager no instalado.")
    print("   Para instalar ejecuta:")
    print("   pip install selenium webdriver-manager\n")

print("\n" + "="*70)
print("🛒 SCRAPER DE OFERTAS - NISSEI Y SHOPPING CHINA 🛒".center(70))
print("="*70 + "\n")

# ======================================================
# FUNCIÓN PARA LIMPIAR PRECIOS
# ======================================================

def limpiar_precio(texto_precio):
    if not texto_precio:
        return None

    texto = texto_precio.strip()

    # ⛔ si no tiene Gs, NO es precio
    if "Gs" not in texto:
        return None

    try:
        limpio = (
            texto.replace("Gs.", "")
                 .replace("Gs", "")
                 .replace(".", "")
                 .replace(",", "")
                 .replace("\xa0", "")
                 .strip()
        )
        return float(limpio)
    except:
        return None


# ======================================================
# SCRAPER DE NISSEI - MEJORADO CON HEADERS COMPLETOS
# ======================================================

def scraper_nissei():
    """Extrae productos de Nissei con headers mejorados para evitar 403"""
    print("🔍 Buscando en Nissei...")
    productos = []
    
    url = "https://nissei.com/py/electronica/celulares-tabletas/celulares-accesorios/telefonos-inteligentes"
    
    try:
        # Headers más completos para evitar detección de bot
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        # Hacer request con delay aleatorio
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"   ⚠️ Error al conectar con Nissei (código {response.status_code})")
            print(f"   💡 Tip: Nissei puede estar bloqueando scrapers. Intenta de nuevo más tarde.\n")
            return productos
        
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("li", class_="product-item")
        
        print(f"   ✓ Encontrados {len(items)} productos")
        
        for item in items:
            try:
                # Título y link
                titulo_tag = item.find("a", class_="product-item-link")
                if not titulo_tag:
                    continue
                    
                titulo = titulo_tag.text.strip()
                link = titulo_tag.get("href", "")
                
                # Precio actual - múltiples métodos
                precio_actual = None
                precio_actual_texto = None
                
                # Método 1: data-price-amount
                precio_tag = item.find("span", attrs={"data-price-amount": True})
                if precio_tag:
                    try:
                        precio_actual = float(precio_tag.get("data-price-amount", 0))
                        precio_span = precio_tag.find("span", class_="price")
                        if precio_span:
                            precio_actual_texto = precio_span.text.strip()
                        else:
                            precio_actual_texto = f"Gs. {precio_actual:,.0f}".replace(",", ".")
                    except:
                        pass
                
                # Método 2: price-final_price
                if not precio_actual:
                    precio_container = item.find("span", class_="price-final_price")
                    if precio_container:
                        precio_span = precio_container.find("span", class_="price")
                        if precio_span:
                            precio_actual_texto = precio_span.text.strip()
                            precio_actual = limpiar_precio(precio_actual_texto)
                
                # Método 3: special-price
                if not precio_actual:
                    precio_special = item.find("span", class_="special-price")
                    if precio_special:
                        precio_span = precio_special.find("span", class_="price")
                        if precio_span:
                            precio_actual_texto = precio_span.text.strip()
                            precio_actual = limpiar_precio(precio_actual_texto)
                
                if not precio_actual:
                    continue
                
                # Precio anterior (old-price)
                precio_anterior_texto = None
                precio_anterior_tag = item.find("span", class_="old-price")
                if precio_anterior_tag:
                    precio_span = precio_anterior_tag.find("span", class_="price")
                    if precio_span:
                        precio_anterior_texto = precio_span.text.strip()
                
                # Agregar producto
                if precio_actual > 0:
                    productos.append({
                        "tienda": "Nissei",
                        "titulo": titulo,
                        "precio_antes": precio_anterior_texto,
                        "precio_ahora": precio_actual_texto,
                        "precio_numero": precio_actual,
                        "link": link
                    })
                    
            except Exception as e:
                continue
        
        print(f"   ✓ Extraídos {len(productos)} productos válidos\n")
        
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    return productos

# ======================================================
# SCRAPER DE SHOPPING CHINA - CORREGIDO
# ======================================================

def scraper_shopping_china():
    """Scraper Shopping China - con título correcto y precio en bruto"""
    if not SELENIUM_DISPONIBLE:
        print("⚠️ Selenium no disponible")
        return []

    print("🔍 Buscando en Shopping China (Selenium)...")
    productos = []

    base_url = "https://www.shoppingchina.com.py"
    url = base_url + "/electronicos"

    driver = None
    try:
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        print("   📥 Iniciando Chrome...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)

        wait = WebDriverWait(driver, 20)
        # Esperar a que cargue la página
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        # Scroll para cargar productos
        for _ in range(4):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Obtener todos los links de productos
        items = driver.find_elements(By.XPATH, "//a[contains(@href, '/producto/')]")
        links = list(dict.fromkeys([i.get_attribute("href") for i in items]))
        
        print(f"   ✓ Productos detectados: {len(links)}")

        # Visitar cada producto
        for idx, link in enumerate(links[:30], 1):  # Limitar a 30 para no tardar mucho
            try:
                print(f"   📦 Procesando {idx}/{min(30, len(links))}...", end='\r')
                driver.get(link)
                time.sleep(1.5)

                # TÍTULO CORRECTO - buscar h1 o el título principal
                titulo = None
                try:
                    # Intento 1: h1 con clase text-uppercase
                    titulo_elem = driver.find_element(By.CSS_SELECTOR, "h1.text-uppercase")
                    titulo = titulo_elem.text.strip()
                except:
                    try:
                        # Intento 2: cualquier h1
                        titulo_elem = driver.find_element(By.TAG_NAME, "h1")
                        titulo = titulo_elem.text.strip()
                    except:
                        pass
                
                # Si el título es "INICIO" o está vacío, buscar en otro lugar
                if not titulo or titulo.upper() == "INICIO":
                    try:
                        # Buscar en el meta title o cualquier otro elemento
                        titulo = driver.title.split("|")[0].strip()
                        if not titulo or "Shopping China" in titulo:
                            titulo = "Producto sin nombre"
                    except:
                        titulo = "Producto sin nombre"

                # PRECIO ACTUAL (en rojo - sc-text-danger)
                try:
                    precio_elem = driver.find_element(By.CLASS_NAME, "sc-text-danger")
                    precio_actual_texto = precio_elem.text.strip()
                except:
                    continue  # Si no hay precio, skip

                precio_actual = limpiar_precio(precio_actual_texto)
                if not precio_actual:
                    continue

                # PRECIO ANTERIOR (en azul - sc-text-primary)
                precio_antes_texto = None
                try:
                    precio_antes_elem = driver.find_element(By.CLASS_NAME, "sc-text-primary")
                    precio_antes_texto = precio_antes_elem.text.strip()
                except:
                    pass

                productos.append({
                    "tienda": "Shopping China",
                    "titulo": titulo,
                    "precio_antes": precio_antes_texto,
                    "precio_ahora": precio_actual_texto,
                    "precio_numero": precio_actual,
                    "link": link
                })

            except Exception as e:
                continue

        print(f"\n   ✓ Extraídos {len(productos)} productos válidos\n")

    except Exception as e:
        print(f"   ✗ Error Shopping China: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

    return productos

# ======================================================
# MOSTRAR RESULTADOS
# ======================================================

def mostrar_ofertas(productos):
    """Muestra las ofertas ordenadas por precio"""
    
    if not productos:
        print("❌ No se encontraron productos.\n")
        return
    
    productos_ordenados = sorted(productos, key=lambda x: x["precio_numero"])
    
    print("="*70)
    print("🔥 MEJORES OFERTAS (Ordenadas por precio) 🔥".center(70))
    print("="*70 + "\n")
    
    for i, producto in enumerate(productos_ordenados[:20], 1):
        print(f"#{i} | {producto['tienda']}")
        print(f"📱 {producto['titulo']}")
        
        if producto['precio_antes']:
            precio_antes = limpiar_precio(producto['precio_antes'])
            if precio_antes and precio_antes > producto['precio_numero']:
                descuento = ((precio_antes - producto['precio_numero']) / precio_antes) * 100
                print(f"💰 Antes: {producto['precio_antes']} → Ahora: {producto['precio_ahora']} (-{descuento:.0f}%)")
            else:
                print(f"💰 Precio: {producto['precio_ahora']}")
        else:
            print(f"💰 Precio: {producto['precio_ahora']}")
        
        if producto['link']:
            print(f"🔗 {producto['link']}")
        print("-" * 70 + "\n")
    
    # Estadísticas
    print("="*70)
    print("📊 RESUMEN".center(70))
    print("="*70)
    
    nissei_count = sum(1 for p in productos if p['tienda'] == 'Nissei')
    shopping_count = sum(1 for p in productos if p['tienda'] == 'Shopping China')
    
    print(f"Nissei: {nissei_count} productos")
    print(f"Shopping China: {shopping_count} productos")
    print(f"Total: {len(productos)} productos")
    
    precios = [p['precio_numero'] for p in productos]
    promedio = sum(precios) / len(precios)
    
    print(f"\nPrecio promedio: Gs. {promedio:,.0f}".replace(",", "."))
    print(f"Precio más bajo: Gs. {min(precios):,.0f}".replace(",", "."))
    print(f"Precio más alto: Gs. {max(precios):,.0f}".replace(",", "."))
    print("="*70 + "\n")

# ======================================================
# MAIN
# ======================================================

def main():
    todos_productos = []

    # Scrapear Nissei
    productos_nissei = scraper_nissei()
    todos_productos.extend(productos_nissei)
    time.sleep(2)

    # Scrapear Shopping China
    productos_china = scraper_shopping_china()
    todos_productos.extend(productos_china)

    # Mostrar resultados
    mostrar_ofertas(todos_productos)
    print("✅ Scraping completado!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrumpido por el usuario\n")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}\n")
        import traceback
        traceback.print_exc()