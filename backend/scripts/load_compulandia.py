import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import get_connection
from app.scraper.compulandia import scrape

conn = get_connection()
cur = conn.cursor()

# obtener store_id
cur.execute("SELECT id FROM store WHERE name='compulandia'")
store_id = cur.fetchone()[0]

products = scrape(limit=10)

for p in products:
    cur.execute("""
        INSERT OR IGNORE INTO listing (store_id, name, url)
        VALUES (?, ?, ?)
    """, (store_id, p["name"], p["url"]))

    cur.execute("SELECT id FROM listing WHERE url=?", (p["url"],))
    listing_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO price_snapshot (listing_id, price_gs)
        VALUES (?, ?)
    """, (listing_id, p["price_gs"]))

conn.commit()
conn.close()

print("✅ Productos insertados")
