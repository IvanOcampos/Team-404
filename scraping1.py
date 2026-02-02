import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict

# Headers para simular un navegador y evitar bloqueos
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_inverfin(url, category):
    """Scraper para Inverfin (basado en estructura típica de Shopify)."""
    products = []
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error al acceder a {url}: {response.status_code}")
        return products
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Ajusta este selector si cambia: contenedor de productos
    product_items = soup.find_all('li', class_='grid__item')
    
    for item in product_items:
        try:
            title_elem = item.find('h3', class_='card__heading')
            title = title_elem.text.strip() if title_elem else 'N/A'
            
            link_elem = item.find('a', class_='full-unstyled-link')
            link = 'https://inverfin.com.py' + link_elem['href'] if link_elem else 'N/A'
            
            image_elem = item.find('img', class_='motion-reduce')
            image = 'https:' + image_elem['src'] if image_elem else 'N/A'
            
            price_div = item.find('div', class_='price')
            regular_price_elem = price_div.find('span', class_='price-item--regular') if price_div else None
            regular_price = regular_price_elem.text.strip() if regular_price_elem else 'N/A'
            
            sale_price_elem = price_div.find('span', class_='price-item--sale') if price_div else None
            sale_price = sale_price_elem.text.strip() if sale_price_elem else regular_price
            
            promo_text = item.find('span', class_='badge--sale')  # O similar para "PROMO"
            promo = promo_text.text.strip() if promo_text else None
            
            if title != 'N/A':
                products.append({
                    'site': 'Inverfin',
                    'category': category,
                    'title': title,
                    'regular_price': regular_price,
                    'sale_price': sale_price,
                    'promo': promo,
                    'link': link,
                    'image': image
                })
        except Exception as e:
            print(f"Error parsing product in Inverfin: {e}")
    
    return products

def scrape_nissei(url, category):
    """Scraper para Nissei (ajusta selectores según inspección)."""
    products = []
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error al acceder a {url}: {response.status_code}")
        return products
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Ajusta: contenedor típico de productos (puede ser 'div.product-item' o similar)
    product_items = soup.find_all('div', class_='product-item')  # Inspecciona para confirmar
    
    for item in product_items:
        try:
            title_elem = item.find('a', class_='product-title')  # O 'h3 a'
            title = title_elem.text.strip() if title_elem else 'N/A'
            link = 'https://nissei.com' + title_elem['href'] if title_elem else 'N/A'
            
            image_elem = item.find('img')
            image = 'https://nissei.com' + image_elem['src'] if image_elem else 'N/A'
            
            regular_price_elem = item.find('span', class_='regular-price')
            regular_price = regular_price_elem.text.strip() if regular_price_elem else 'N/A'
            
            sale_price_elem = item.find('span', class_='special-price')
            sale_price = sale_price_elem.text.strip() if sale_price_elem else regular_price
            
            promo_elem = item.find('span', class_='discount')  # Para %-off
            promo = promo_elem.text.strip() if promo_elem else None
            
            if title != 'N/A':
                products.append({
                    'site': 'Nissei',
                    'category': category,
                    'title': title,
                    'regular_price': regular_price,
                    'sale_price': sale_price,
                    'promo': promo,
                    'link': link,
                    'image': image
                })
        except Exception as e:
            print(f"Error parsing product in Nissei: {e}")
    
    return products

def scrape_bristol(url, category):
    """Scraper para Bristol (ajusta selectores según inspección)."""
    products = []
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error al acceder a {url}: {response.status_code}")
        return products
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Ajusta: contenedor típico (puede ser 'div.product-block' o similar)
    product_items = soup.find_all('div', class_='product-block')
    
    for item in product_items:
        try:
            title_elem = item.find('h2', class_='product-name')  # O 'a' con title
            title = title_elem.text.strip() if title_elem else 'N/A'
            
            link_elem = item.find('a', class_='product-link')
            link = 'https://www.bristol.com.py' + link_elem['href'] if link_elem else 'N/A'
            
            image_elem = item.find('img', class_='product-image')
            image = image_elem['src'] if image_elem else 'N/A'
            
            regular_price_elem = item.find('span', class_='old-price')
            regular_price = regular_price_elem.text.strip() if regular_price_elem else 'N/A'
            
            sale_price_elem = item.find('span', class_='price')
            sale_price = sale_price_elem.text.strip() if sale_price_elem else regular_price
            
            promo_elem = item.find('div', class_='sale-label')
            promo = promo_elem.text.strip() if promo_elem else None
            
            if title != 'N/A':
                products.append({
                    'site': 'Bristol',
                    'category': category,
                    'title': title,
                    'regular_price': regular_price,
                    'sale_price': sale_price,
                    'promo': promo,
                    'link': link,
                    'image': image
                })
        except Exception as e:
            print(f"Error parsing product in Bristol: {e}")
    
    return products

def get_best_offers(products):
    """Encuentra los mejores precios/ofertas: productos con promo, ordenados por precio de venta ascendente."""
    offers = [p for p in products if p['promo'] or p['sale_price'] != p['regular_price']]
    offers_sorted = sorted(offers, key=lambda x: float(x['sale_price'].replace('Gs. ', '').replace('.', '').replace(',', '.')) if 'Gs.' in x['sale_price'] else float('inf'))
    return offers_sorted

def main():
    # URLs de categorías (actualiza si cambian)
    urls = {
        'celulares': {
            'inverfin': 'https://inverfin.com.py/collections/smartphones',
            'nissei': 'https://nissei.com/py/electronica/celulares-tabletas/celulares-accesorios/telefonos-inteligentes',
            'bristol': 'https://www.bristol.com.py/celulares-y-smartwatches/celulares'
        },
        'auriculares': {
            'inverfin': 'https://inverfin.com.py/collections/auriculares',
            'nissei': 'https://nissei.com/py/electronica/audio-y-video/auriculares',
            'bristol': 'https://www.bristol.com.py/celulares-y-smartwatches/accesorios-de-celulares/auriculares'
        }
    }
    
    all_products = []
    
    for category, sites in urls.items():
        for site, url in sites.items():
            if site == 'inverfin':
                all_products.extend(scrape_inverfin(url, category))
            elif site == 'nissei':
                all_products.extend(scrape_nissei(url, category))
            elif site == 'bristol':
                all_products.extend(scrape_bristol(url, category))
            time.sleep(2)  # Delay para no sobrecargar
    
    # Obtener mejores ofertas
    best_offers = get_best_offers(all_products)
    
    # Mostrar resultados
    print("Mejores ofertas y precios bajos encontrados:")
    for product in best_offers:
        print(f"Site: {product['site']} | Categoría: {product['category']} | Título: {product['title']}")
        print(f"Precio regular: {product['regular_price']} | Precio oferta: {product['sale_price']} | Promo: {product['promo']}")
        print(f"Link: {product['link']} | Imagen: {product['image']}")
        print("---")
    
    # Opcional: guardar en CSV
    # import csv
    # with open('ofertas_electronicas.csv', 'w', newline='', encoding='utf-8') as f:
    #     writer = csv.DictWriter(f, fieldnames=best_offers[0].keys())
    #     writer.writeheader()
    #     writer.writerows(best_offers)

if __name__ == "__main__":
    main()
