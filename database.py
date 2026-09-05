import sqlite3
import datetime
import os
from typing import List, Dict

DB_PATH = "modawen.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            topic TEXT,
            title TEXT,
            wp_post_id INTEGER,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_article(topic: str, title: str, wp_post_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO generated_articles (timestamp, topic, title, wp_post_id, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.datetime.now().isoformat(), topic, title, wp_post_id, status))
    conn.commit()
    conn.close()

def get_stats() -> Dict:
    if not os.path.exists(DB_PATH):
        return {"total": 0, "success": 0, "rate": 0}
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM generated_articles")
    total_generated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM generated_articles WHERE status = 'Success'")
    total_success = cursor.fetchone()[0]
    
    conn.close()
    
    success_rate = 0
    if total_generated > 0:
        success_rate = (total_success / total_generated) * 100
        
    return {
        "total": total_generated,
        "success": total_success,
        "rate": round(success_rate, 2)
    }

def get_recent_logs(limit: int = 50) -> List[Dict]:
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM generated_articles ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
