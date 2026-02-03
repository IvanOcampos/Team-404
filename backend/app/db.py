import sqlite3
from pathlib import Path

DB_PATH = Path("data/dealhunter.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)
