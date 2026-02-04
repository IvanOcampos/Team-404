from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def analizar_pagina(url_objetivo):
    print(f"\n🕵️  ANALIZANDO: {url_objetivo}")
    print("-" * 60)

    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        print("⏳ [1/4] Cargando página...")
        driver.get(url_objetivo)
        time.sleep(8) 

        # --- ESTRATEGIA 1: Texto (Gs, $) ---
        print("🔍 [2/4] Buscando precios por texto (Gs, $)...")
        xpath_texto = "//*[contains(text(), 'Gs') or contains(text(), 'PYG') or contains(text(), '$')]"
        elementos = driver.find_elements(By.XPATH, xpath_texto)
        visibles = [e for e in elementos if e.is_displayed() and len(e.text) < 50]

        # --- ESTRATEGIA 2: Clases CSS (Plan B para TecnoStore/WooCommerce) ---
        if not visibles:
            print("⚠️ No encontré texto moneda. Activando PLAN B (Búsqueda por Clases CSS)...")
            # Buscamos clases comunes de e-commerce
            selectores_precio = [".price", ".amount", ".special-price", ".regular-price", "span.woocommerce-Price-amount"]
            
            for selector in selectores_precio:
                elementos_css = driver.find_elements(By.CSS_SELECTOR, selector)
                # Filtramos visibles
                candidatos = [e for e in elementos_css if e.is_displayed() and any(char.isdigit() for char in e.text)]
                if candidatos:
                    print(f"   -> ¡Éxito! Encontrados precios con la clase: '{selector}'")
                    visibles = candidatos
                    break

        print(f"   -> Total encontrados: {len(visibles)}")

        if not visibles:
            print("❌ IMPOSIBLE DETECTAR PRECIOS AUTOMÁTICAMENTE.")
            return

        # Seleccionamos el 2do o 1ro
        target = visibles[1] if len(visibles) > 1 else visibles[0]
        
        print("\n🧬 [3/4] REPORTE DE ESTRUCTURA")
        print(f"   Texto detectado: '{target.text}'")
        print("-" * 60)

        elemento_actual = target
        niveles = ["Precio (Hijo)", "Padre", "Abuelo", "Bisabuelo", "Tatarabuelo"]
        
        for nivel in niveles:
            tag = elemento_actual.tag_name
            clases = elemento_actual.get_attribute("class") or "(Sin clase)"
            print(f"   📍 {nivel:<15}: <{tag}> class='{clases}'")
            try:
                elemento_actual = elemento_actual.find_element(By.XPATH, "./..")
            except: break
        
        print("-" * 60)
        print("✅ Busca en la lista de arriba la clase que parezca el contenedor.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("\n" + "="*50)
    print(" 🕵️  HERRAMIENTA DE INGENIERÍA INVERSA V2")
    print("="*50)
    while True:
        url_input = input("\n🔗 URL (o 'salir'): ").strip()
        if url_input.lower() == 'salir': break
        if not url_input.startswith("http"): continue
            
        # Llamamos a la función con lo que escribió el usuario
        analizar_pagina(url_input)