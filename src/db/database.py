import sqlite3
from pathlib import Path
from src.models.session import SessionRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS learning_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    start_timestamp DATETIME NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    focus_level INTEGER NOT NULL CHECK (focus_level BETWEEN 1 AND 5),
    test_score INTEGER CHECK (test_score BETWEEN 0 AND 100),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_date ON learning_sessions(start_timestamp);
"""

class DatabaseManager:
    def __init__(self):
        self.db_path = "data/database.sqlite"

    def _connect(self):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row 
            return conn
    
    def migrate(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.executescript(SCHEMA)
            conn.commit()
        finally:
            conn.close()
    
    def add_session(self, session):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO learning_sessions (subject_id, start_timestamp, duration_minutes, focus_level, test_score, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """, session.to_tuple())
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()
    def get_session(self, session_id):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM learning_sessions WHERE id = ?
                """, (session_id,))
            row = cur.fetchone()
            if row:
                return SessionRecord.from_row(row)
            return None
        finally:
            conn.close()
    def list_sessions(self, limit = 10):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM learning_sessions ORDER BY start_timestamp DESC LIMIT ?
                """, (limit,))
            rows = cur.fetchall()
            return [SessionRecord.from_row(row) for row in rows]
        finally:
            conn.close()