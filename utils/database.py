import sqlite3
import os
from typing import Optional
from utils.paths import DATA_DB_PATH, ensure_data_dirs

class Database:
    def __init__(self, db_path: str = DATA_DB_PATH):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_db_dir()
        self.connect()
        self.init_tables()

    def _ensure_db_dir(self):
        ensure_data_dirs()
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def init_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                job_type TEXT,
                location TEXT,
                work_mode TEXT,
                salary_min TEXT,
                salary_max TEXT,
                company_size TEXT,
                industry TEXT,
                job_url TEXT,
                notes TEXT,
                status TEXT DEFAULT 'wishlist',
                contacted INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._ensure_column("companies", "contacted", "INTEGER NOT NULL DEFAULT 0")
        self._ensure_column("companies", "contact_name", "TEXT")
        self._ensure_column("companies", "contact_email", "TEXT")
        self._ensure_column("companies", "contact_phone", "TEXT")

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                date_applied TEXT,
                status TEXT DEFAULT 'applied',
                follow_up_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT,
                style TEXT DEFAULT 'modern',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS personal_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                linkedin TEXT,
                github TEXT,
                website TEXT,
                address TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_text TEXT,
                company_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def _ensure_column(self, table: str, column: str, definition: str):
        columns = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        if column not in {row["name"] for row in columns}:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def execute(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetch_all(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def close(self):
        if self.conn:
            self.conn.close()

_db_instance = None

def get_db(db_path: str = DATA_DB_PATH) -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance
