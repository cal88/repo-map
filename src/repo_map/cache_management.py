import sqlite3
import os
import json
from typing import List, Dict, Any

def load_cache(repo_root: str, db_name: str = '.repo-map-cache.db') -> sqlite3.Connection:
    cache_file_path = os.path.join(repo_root, db_name)
    conn = sqlite3.connect(cache_file_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            path TEXT PRIMARY KEY,
            hash TEXT,
            description TEXT,
            developer_consideration TEXT,
            imports TEXT,
            functions TEXT
        )
    """)
    
    cursor.execute("PRAGMA table_info(cache)")
    existing_columns = [info[1] for info in cursor.fetchall()]
    
    new_columns = {
        'developer_consideration',
    }
    
    for column in new_columns:
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE cache ADD COLUMN {column} TEXT")
    
    conn.commit()
    return conn
