"""
WEB SCRAPER - Comparador de Precios
Nissei: requests + BeautifulSoup
sho: Selenium con webdriver-manager (sin necesidad de descargar ChromeDriver)
"""

import requests
from bs4 import BeautifulSoup
import time

# Para SmartHouse necesitamos Selenium
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
# SCRAPER DE NISSEI
# ======================================================

def scraper_nissei():
    """Extrae productos de Nissei"""
    print("🔍 Buscando en Nissei...")
    productos = []
    
    url = "https://nissei.com/py/electronica/celulares-tabletas/celulares-accesorios/telefonos-inteligentes"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"   ⚠️ Error al conectar con Nissei (código {response.status_code})")
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
# SCRAPER DE SMARTHOUSE - CON SELENIUM + WEBDRIVER-MANAGER
# ======================================================

# ======================================================
# SCRAPER DE SHOPPING CHINA - ELECTRÓNICOS
# ======================================================
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ==========================
# CONFIGURACIÓN DEL NAVEGADOR
# ==========================
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecuta Chrome sin abrir ventana
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Cambia la ruta según tu chromedriver
driver_path = r"C:\Users\learn\OneDrive\Desktop\proyectp_hakaton\Team-404\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# ==========================
# URL DE ALEX
# ==========================
url_alex = "https://www.alex.com.py/categoria/1/celulares-y-accesorios?marcas=&categorias=&categorias_top="
driver.get(url_alex)

# ==========================
# ESPERAR QUE CARGUEN PRODUCTOS
# ==========================
wait = WebDriverWait(driver, 15)  # Espera máxima 15s
try:
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.producto_item")))
except:
    print("❌ No se cargaron productos en Alex")
    driver.quit()
    exit()

# ==========================
# EXTRAER PRODUCTOS
# ==========================
productos = driver.find_elements(By.CSS_SELECTOR, "div.producto_item")
lista_productos = []

for producto in productos:
    try:
        titulo = producto.find_element(By.CSS_SELECTOR, "h2.producto_nombre a").text.strip()
        link = producto.find_element(By.CSS_SELECTOR, "h2.producto_nombre a").get_attribute("href")
        precio = producto.find_element(By.CSS_SELECTOR, "span.precio").text.strip()
        
        lista_productos.append({
            "titulo": titulo,
            "link": link,
            "precio": precio
        })
    except:
        # Saltar productos sin precio o título
        continue

driver.quit()

# ==========================
# MOSTRAR RESULTADOS
# ==========================
if lista_productos:
    print(f"✓ Productos encontrados: {len(productos)}")
    print(f"✓ Extraídos {len(lista_productos)} productos válidos\n")
    
    print("🔥 MEJORES OFERTAS (Ordenadas por precio) 🔥")
    for i, p in enumerate(lista_productos, 1):
        print(f"#{i} | Alex")
        print(f"📱 {p['titulo']}")
        print(f"💰 Precio: {p['precio']}")
        print(f"🔗 {p['link']}")
        print("----------------------------------------------------------------------")
else:
    print("❌ No se encontraron productos.")





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
    smarthouse_count = sum(1 for p in productos if p['tienda'] == 'SmartHouse')
    
    print(f"Nissei: {nissei_count} productos")
    print(f"SmartHouse: {smarthouse_count} productos")
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

    productos_nissei = scraper_nissei()
    todos_productos.extend(productos_nissei)
    time.sleep(2)

    productos_china = scrap()
    todos_productos.extend(productos_china)

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