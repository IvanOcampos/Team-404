import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tablas:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT * FROM store;")
print("Stores:", cur.fetchall())

conn.close()
