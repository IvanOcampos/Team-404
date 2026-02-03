import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS store (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  base_url TEXT
);

CREATE TABLE IF NOT EXISTS listing (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  store_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  FOREIGN KEY(store_id) REFERENCES store(id)
);

CREATE TABLE IF NOT EXISTS price_snapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  listing_id INTEGER NOT NULL,
  price_gs INTEGER NOT NULL,
  captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(listing_id) REFERENCES listing(id)
);

INSERT OR IGNORE INTO store(name, base_url)
VALUES ('compulandia', 'https://www.compulandia.com.py');
""")
    
conn.commit()
conn.close()

print("✅ Base de datos creada correctamente")
