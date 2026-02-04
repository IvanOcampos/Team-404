import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote_plus
from database import SessionLocal
import models

HEADERS_GLOBAL = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "es-419,es;q=0.9",
}

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    SELENIUM_DISPONIBLE = True
except ImportError:
    SELENIUM_DISPONIBLE = False

# ======================================================
# UTILIDADES
# ======================================================
def limpiar_precio(texto_precio):
    if not texto_precio: return None
    texto = str(texto_precio).strip().lower()
    # Limpieza agresiva de basura
    texto = texto.replace("gs.", "").replace("gs", "").replace("pyg", "").replace("us$", "")
    texto = texto.replace("precio", "").replace("contado", "").replace("lista", "").replace("internet", "")
    texto = texto.replace(".", "").replace(",", ".").replace("\xa0", "").strip()
    try:
        match = re.search(r"(\d+(\.\d+)?)", texto)
        if match:
            val = float(match.group(1))
            return val if val > 5000 else None
        return None
    except: return None

# ======================================================
# GUARDADO EN DB (Con Filtro Anti-Basura)
# ======================================================
def enviar_al_backend(producto_data, origen="web"):
    if not producto_data['name'] or not producto_data['initial_price']: 
        return None
    
    # --- FILTRO DE CALIDAD ---
    nombre_lower = producto_data['name'].lower()
    
    # 1. Palabras prohibidas (botones capturados por error)
    basura = ["añadir", "carrito", "comprar", "vista rápida", "add to cart", "seleccionar opciones", "leer más"]
    if any(b in nombre_lower for b in basura):
        return None

    # 2. Si el nombre es demasiado corto (ej: "A") o demasiado largo (error de parseo)
    if len(nombre_lower) < 3 or len(nombre_lower) > 200:
        return None

    db = SessionLocal()
    product_id = None
    try:
        existing_product = db.query(models.Product).filter(models.Product.url == producto_data['url']).first()
        
        if existing_product:
            product_id = existing_product.id
            if origen == "web": 
                existing_product.source = "web"
        else:
            new_product = models.Product(
                name=producto_data['name'],
                url=producto_data['url'],
                image_url=producto_data['image_url'],
                source=origen
            )
            db.add(new_product)
            db.commit()
            db.refresh(new_product)
            product_id = new_product.id

        new_price = models.Price(
            amount=producto_data['initial_price'],
            store=producto_data['store'],
            product_id=product_id
        )
        db.add(new_price)
        db.commit()
        return product_id

    except Exception as e:
        print(f"   ❌ Error DB: {e}")
        db.rollback()
        return None
    finally:
        db.close()

# ======================================================
# BÚSQUEDA
# ======================================================
def buscar_productos_en_web(keyword, origen="web"):
    print(f"\n🔍 BÚSQUEDA ({origen}): '{keyword}'")
    found_ids = []
    q = quote_plus(keyword)

    # 1. TIENDAS REQUESTS (Nissei y CellShop suelen ser estables)
    tiendas_fast = [
        {"nombre": "Nissei", "url": f"https://nissei.com/py/catalogsearch/result/?q={q}", "card": "li.product-item", "name": "a.product-item-link", "price": "[data-price-amount]", "img": "img.product-image-photo"},
        {"nombre": "CellShop", "url": f"https://cellshop.com.py/catalogsearch/result/?q={q}", "card": ".product-item-info", "name": ".product-item-link", "price": ".price", "img": "img"}
    ]

    for t in tiendas_fast:
        try:
            res = requests.get(t['url'], headers=HEADERS_GLOBAL, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(t['card'])
            for item in items[:5]:
                try:
                    name = item.select_one(t['name']).text.strip()
                    link_tag = item.select_one(t['name'])
                    link = link_tag['href'] if link_tag.has_attr('href') else item.find("a")['href']
                    price = limpiar_precio(item.select_one(t['price']).text)
                    img = item.select_one(t['img'])['src'] if item.select_one(t['img']) else None
                    if price:
                        pid = enviar_al_backend({"name": name, "url": link, "initial_price": price, "store": t['nombre'], "image_url": img}, origen)
                        if pid and pid not in found_ids: found_ids.append(pid)
                except: continue
        except: pass

    # 2. TIENDAS SELENIUM (Aquí estaba el problema)
    if SELENIUM_DISPONIBLE:
        options = Options()
        options.add_argument("--headless=new") 
        options.add_argument("--log-level=3")
        try:
            driver = webdriver.Chrome(options=options)
            
            tiendas_selenium = [
                {"nombre": "TiendaMovil", "url": f"https://tiendamovil.com.py/?s={q}&post_type=product"},
                {"nombre": "TopTechnology", "url": f"https://toptechnology.com.py/?s={q}&post_type=product"}
            ]

            for t in tiendas_selenium:
                driver.get(t['url'])
                time.sleep(3) # Espera vital
                
                # Buscamos las tarjetas
                items = driver.find_elements(By.CSS_SELECTOR, "article.product-miniature, div.product-grid-item, .product-type-simple, .product-small")
                
                for item in items[:6]:
                    try:
                        # --- EXTRACCIÓN DEL PRECIO ---
                        # Buscamos números en todo el texto del item
                        texto_completo = item.text.split('\n')
                        precio = None
                        for linea in texto_completo:
                            p = limpiar_precio(linea)
                            if p: 
                                precio = p; break
                        if not precio: continue

                        # --- EXTRACCIÓN DEL TÍTULO Y LINK (ESPECÍFICA POR TIENDA) ---
                        titulo = ""
                        link = ""

                        if t['nombre'] == "TopTechnology":
                            # TopTech usa: <h2 class="woocommerce-loop-product__title">Nombre</h2>
                            try:
                                # Intento 1: Selector específico de WooCommerce
                                elem = item.find_element(By.CSS_SELECTOR, ".woocommerce-loop-product__title, h2.product-title")
                                titulo = elem.text
                                # El link suele envolver la imagen o el título
                                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                            except:
                                # Fallback
                                tag_a = item.find_element(By.TAG_NAME, "a")
                                titulo = tag_a.text
                                link = tag_a.get_attribute("href")

                        elif t['nombre'] == "TiendaMovil":
                            # TiendaMovil usa: <h3 class="product-title"><a href="...">Nombre</a></h3>
                            try:
                                # Buscamos DIRECTAMENTE el título dentro de h3.product-title
                                title_container = item.find_element(By.CSS_SELECTOR, "h3.product-title, .product-title")
                                tag_a = title_container.find_element(By.TAG_NAME, "a")
                                titulo = tag_a.text # Texto limpio del enlace
                                link = tag_a.get_attribute("href")
                            except:
                                # Fallback
                                tag_a = item.find_element(By.TAG_NAME, "a")
                                titulo = tag_a.text
                                link = tag_a.get_attribute("href")
                        
                        else:
                            # Genérico
                            tag_a = item.find_element(By.TAG_NAME, "a")
                            titulo = tag_a.text
                            link = tag_a.get_attribute("href")

                        # Limpieza final del título por si acaso
                        if not titulo or len(titulo) < 3: continue

                        # --- IMAGEN ---
                        img = None
                        try: img = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                        except: pass
                        
                        # --- ENVIAR ---
                        pid = enviar_al_backend({"name": titulo, "url": link, "initial_price": precio, "store": t['nombre'], "image_url": img}, origen)
                        if pid and pid not in found_ids: found_ids.append(pid)

                    except Exception as e:
                        continue # Si falla un producto, sigue al siguiente
        except Exception as e:
            print(f"Error Selenium: {e}")
        finally: 
            if 'driver' in locals(): driver.quit()
    
    print(f"✅ Búsqueda finalizada. Encontrados: {len(found_ids)}")
    return found_ids