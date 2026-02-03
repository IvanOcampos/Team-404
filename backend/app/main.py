from fastapi import FastAPI, Query
from pathlib import Path
import sqlite3

app = FastAPI(title="DealHunter API", version="0.1.0")

DB_PATH = Path("data/dealhunter.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health():
    # confirma que la DB existe y que se puede consultar
    with get_conn() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "db": "connected"}

@app.get("/search")
def search(
    q: str = Query(default="", description="Texto a buscar"),
    limit: int = Query(default=20, ge=1, le=100)
):
    q_norm = f"%{q.strip().lower()}%"

    sql = """
    SELECT
      l.id,
      s.name AS store,
      l.name,
      l.url,
      (
        SELECT ps.price_gs
        FROM price_snapshot ps
        WHERE ps.listing_id = l.id
        ORDER BY ps.captured_at DESC
        LIMIT 1
      ) AS price_gs,
      (
        SELECT ps.captured_at
        FROM price_snapshot ps
        WHERE ps.listing_id = l.id
        ORDER BY ps.captured_at DESC
        LIMIT 1
      ) AS captured_at
    FROM listing l
    JOIN store s ON s.id = l.store_id
    WHERE lower(l.name) LIKE ?
    ORDER BY price_gs ASC
    LIMIT ?
    """

    with get_conn() as conn:
        rows = conn.execute(sql, (q_norm, limit)).fetchall()

    items = []
    for r in rows:
        items.append({
            "store": r["store"],
            "name": r["name"],
            "url": r["url"],
            "price_gs": r["price_gs"],
            "captured_at": r["captured_at"],
            "is_deal": False,
            "deal_reason": None,
        })

    return {"query": q, "count": len(items), "items": items}
