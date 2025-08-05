import sqlite3
from typing import Optional

def create_connection(db_file="knowledge.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            raw_text TEXT,
            summary TEXT,
            cluster_label INTEGER,
            depth INTEGER
        )
    """)
    return conn

def insert_entry(
    conn: sqlite3.Connection,
    title: str,
    url: str,
    raw_text: str,
    summary: str,
    cluster_label: Optional[int] = None,
    depth: int = 0
):
    conn.execute("""
        INSERT INTO knowledge (title, url, raw_text, summary, cluster_label, depth)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, url, raw_text, summary, cluster_label, depth))
    conn.commit()
