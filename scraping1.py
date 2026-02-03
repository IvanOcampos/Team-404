"""
WEB SCRAPER SIMPLE - Comparador de Precios
Versión actualizada con selectores correctos para Nissei y SmartHouse
"""

import requests
from bs4 import BeautifulSoup
import time

print("\n" + "="*70)
print("🛒 SCRAPER DE OFERTAS - NISSEI Y SMARTHOUSE 🛒".center(70))
print("="*70 + "\n")

# ======================================================
# FUNCIÓN PARA LIMPIAR PRECIOS
# ======================================================

def limpiar_precio(texto_precio):
    """Convierte 'Gs. 1.500.000' en 1500000.0"""
    if not texto_precio:
        return None
    try:
        # Quitar Gs., Gs, puntos, espacios y &nbsp;
        limpio = texto_precio.replace("Gs.", "").replace("Gs", "")
        limpio = limpio.replace(".", "").replace(",", ".").replace("\xa0", "").strip()
        return float(limpio)
    except:
        return None

# ======================================================
# SCRAPER DE NISSEI - ACTUALIZADO
# ======================================================

def scraper_nissei():
    """Extrae productos de Nissei con selectores actualizados"""
    print("🔍 Buscando en Nissei...")
    productos = []
    
    url = "https://nissei.com"
    
    try:
        # Hacer request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"   ⚠️ Error al conectar con Nissei (código {response.status_code})")
            return productos
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("li", class_="product-item")
        
        print(f"   ✓ Encontrados {len(items)} productos")
        
        # Extraer datos de cada producto
        for item in items:
            try:
                # Título
                titulo_tag = item.find("a", class_="product-item-link")
                if not titulo_tag:
                    continue
                    
                titulo = titulo_tag.text.strip()
                link = titulo_tag.get("href", "")
                
                # NUEVO: Buscar precio usando el selector actualizado
                # Buscar span con atributo data-price-amount
                precio_oferta_tag = item.find("span", attrs={"data-price-amount": True})
                
                if not precio_oferta_tag:
                    # Fallback al método anterior si no encuentra el nuevo
                    precio_oferta_tag = item.find("span", class_="special-price")
                    if precio_oferta_tag:
                        precio_oferta_span = precio_oferta_tag.find("span", class_="price")
                        if precio_oferta_span:
                            precio_oferta_texto = precio_oferta_span.text.strip()
                        else:
                            continue
                    else:
                        continue
                else:
                    # Obtener el precio del atributo data-price-amount
                    precio_oferta_numero = float(precio_oferta_tag.get("data-price-amount", 0))
                    # También obtener el texto visible del precio
                    precio_span = precio_oferta_tag.find("span", class_="price")
                    if precio_span:
                        precio_oferta_texto = precio_span.text.strip()
                    else:
                        precio_oferta_texto = f"Gs. {precio_oferta_numero:,.0f}".replace(",", ".")
                
                precio_oferta = limpiar_precio(precio_oferta_texto) if 'precio_oferta_texto' in locals() else precio_oferta_numero
                
                # Precio regular (old-price)
                precio_regular_tag = item.find("span", class_="old-price")
                precio_regular_texto = None
                precio_regular = None
                
                if precio_regular_tag:
                    precio_regular_span = precio_regular_tag.find("span", class_="price")
                    if precio_regular_span:
                        precio_regular_texto = precio_regular_span.text.strip()
                        precio_regular = limpiar_precio(precio_regular_texto)
                
                # Solo agregar si tiene precio válido
                if precio_oferta and precio_oferta > 0:
                    productos.append({
                        "tienda": "Nissei",
                        "titulo": titulo,
                        "precio_antes": precio_regular_texto,
                        "precio_ahora": precio_oferta_texto if 'precio_oferta_texto' in locals() else f"Gs. {precio_oferta:,.0f}".replace(",", "."),
                        "precio_numero": precio_oferta,
                        "link": link
                    })
                    
            except Exception as e:
                continue
        
        print(f"   ✓ Extraídos {len(productos)} productos con precios válidos\n")
        
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    return productos

# ======================================================
# SCRAPER DE SMARTHOUSE - ACTUALIZADO
# ======================================================

def scraper_smarthouse():
    """Extrae productos de SmartHouse con selectores actualizados"""
    print("🔍 Buscando en SmartHouse...")
    productos = []
    
    url = "https://www.smarthouse.com.py"
    
    try:
        # Hacer request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"   ⚠️ Error al conectar con SmartHouse (código {response.status_code})")
            return productos
        
        # Parsear HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # NUEVO: Buscar títulos con la clase correcta
        titulos = soup.find_all("h1", class_="fw-semibold")
        
        print(f"   ✓ Encontrados {len(titulos)} productos")
        
        # Extraer datos de cada producto
        for titulo_tag in titulos:
            try:
                # El título está en el h1
                titulo = titulo_tag.text.strip()
                
                # Buscar el contenedor padre que tiene todos los datos
                contenedor = titulo_tag.parent
                
                # Buscar hasta 3 niveles arriba para encontrar el div principal
                for _ in range(3):
                    if contenedor and contenedor.parent:
                        contenedor = contenedor.parent
                
                # Buscar link
                link_tag = contenedor.find("a") if contenedor else None
                link = ""
                if link_tag:
                    link = link_tag.get("href", "")
                    if link and not link.startswith("http"):
                        link = "https://www.smarthouse.com.py" + link
                
                # NUEVO: Precio actual - buscar span con fw-bold text-primary
                precio_actual_tag = contenedor.find("span", class_=["fw-bold", "text-primary"]) if contenedor else None
                
                # Fallback: buscar h4 text-primary
                if not precio_actual_tag and contenedor:
                    precio_actual_tag = contenedor.find("h4", class_="text-primary")
                
                if not precio_actual_tag:
                    continue
                    
                precio_actual_texto = precio_actual_tag.text.strip()
                precio_actual = limpiar_precio(precio_actual_texto)
                
                # NUEVO: Precio anterior - buscar h4 con text-muted
                precio_viejo_tag = contenedor.find("h4", class_="text-muted") if contenedor else None
                
                precio_viejo_texto = None
                if precio_viejo_tag:
                    precio_viejo_texto = precio_viejo_tag.text.strip()
                
                # Solo agregar si tiene precio válido
                if precio_actual and precio_actual > 0:
                    productos.append({
                        "tienda": "SmartHouse",
                        "titulo": titulo,
                        "precio_antes": precio_viejo_texto,
                        "precio_ahora": precio_actual_texto,
                        "precio_numero": precio_actual,
                        "link": link
                    })
                    
            except Exception as e:
                continue
        
        # Eliminar duplicados
        productos_unicos = []
        vistos = set()
        
        for p in productos:
            clave = (p["titulo"], p["precio_numero"])
            if clave not in vistos:
                vistos.add(clave)
                productos_unicos.append(p)
        
        print(f"   ✓ Extraídos {len(productos_unicos)} productos únicos\n")
        return productos_unicos
        
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return productos

# ======================================================
# MOSTRAR RESULTADOS
# ======================================================

def mostrar_ofertas(productos):
    """Muestra las ofertas ordenadas por precio"""
    
    if not productos:
        print("❌ No se encontraron productos.\n")
        return
    
    # Ordenar por precio (de menor a mayor)
    productos_ordenados = sorted(productos, key=lambda x: x["precio_numero"])
    
    print("="*70)
    print("🔥 MEJORES OFERTAS (Ordenadas por precio) 🔥".center(70))
    print("="*70 + "\n")
    
    # Mostrar top 20
    for i, producto in enumerate(productos_ordenados[:20], 1):
        print(f"#{i} | {producto['tienda']}")
        print(f"📱 {producto['titulo']}")
        
        # Calcular descuento si hay precio anterior
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
    
    # Contar por tienda
    nissei_count = sum(1 for p in productos if p['tienda'] == 'Nissei')
    smarthouse_count = sum(1 for p in productos if p['tienda'] == 'SmartHouse')
    
    print(f"Nissei: {nissei_count} productos")
    print(f"SmartHouse: {smarthouse_count} productos")
    print(f"Total: {len(productos)} productos")
    print(f"Mostrando top 20")
    
    precios = [p['precio_numero'] for p in productos]
    promedio = sum(precios) / len(precios)
    
    print(f"\nPrecio promedio: Gs. {promedio:,.0f}".replace(",", "."))
    print(f"Precio más bajo: Gs. {min(precios):,.0f}".replace(",", "."))
    print(f"Precio más alto: Gs. {max(precios):,.0f}".replace(",", "."))
    print("="*70 + "\n")

# ======================================================
# MAIN - EJECUTAR TODO
# ======================================================

def main():
    """Función principal"""
    
    todos_productos = []
    
    # Scrapear Nissei
    productos_nissei = scraper_nissei()
    todos_productos.extend(productos_nissei)
    time.sleep(2)  # Esperar 2 segundos entre requests
    
    # Scrapear SmartHouse
    productos_smarthouse = scraper_smarthouse()
    todos_productos.extend(productos_smarthouse)
    
    # Mostrar resultados
    mostrar_ofertas(todos_productos)
    
    print("✅ Scraping completado!\n")

# Ejecutar el scraper
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrumpido por el usuario\n")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}\n")
