import os
import sqlite3
from pathlib import Path
from src.models.session import SessionRecord
from src.models.subject import Subject

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
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = os.environ.get("DB_PATH", "data/database.sqlite")
        self.db_path = db_path
        p = Path(self.db_path)
        if p.parent and not p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)

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
    def add_subject(self, name: str):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_subjects(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM subjects ORDER BY name")
            rows = cur.fetchall()
            return [Subject(id=row["id"], name=row["name"]) for row in rows]
        finally:
            conn.close()
    def get_subject(self, subject_id: int):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
            row = cur.fetchone()
            if row:
                return Subject(id=row["id"], name=row["name"])
            return None
        finally:
            conn.close()

    def update_subject(self, subject_id: int, name: str):
        if not name or not name.strip():
            raise ValueError("Subject name must be a non-empty string")
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE subjects SET name = ? WHERE id = ?", (name, subject_id))
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    def delete_subject(self, subject_id: int):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
            conn.commit()
            return cur.rowcount
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
    def update_session(self, session: SessionRecord):
        if session.id is None:
            raise ValueError("session.id is required to update a session")
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE learning_sessions
                SET subject_id = ?, start_timestamp = ?, duration_minutes = ?, focus_level = ?, test_score = ?, notes = ?
                WHERE id = ?
                """,
                (
                    session.subject_id,
                    session.get_start_timestamp(),
                    session.duration_minutes,
                    session.focus_level,
                    session.test_score,
                    session.notes,
                    session.id,
                ),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()

    def delete_session(self, session_id: int):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM learning_sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cur.rowcount
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
    def get_sessions(self, limit: int = 10):
        return self.list_sessions(limit=limit)