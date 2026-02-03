import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.compulandia.com.py/categoria-producto/celulares/"

def parse_price(text):
    m = re.search(r"Gs\.\s*([\d\.]+)", text)
    return int(m.group(1).replace(".", "")) if m else None

def scrape(limit=10):
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    products = soup.select("li.product")

    for p in products[:limit]:
        a = p.select_one("a[href]")
        price_el = p.select_one(".price")

        if not a or not price_el:
            continue

        items.append({
            "name": a.get_text(strip=True),
            "url": a["href"],
            "price_gs": parse_price(price_el.get_text())
        })

    return items
