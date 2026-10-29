"""
Database persistence module for ParkVision AI.
Uses Python standard library sqlite3.
Handles users, analysis history, and user feedback.
Safe for concurrent startup across multiple sessions.
"""

import os
import sqlite3
import tempfile
import threading
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

_db_lock = threading.Lock()
_SHARED_DB_PATH: Optional[Path] = None


def _resolve_default_db_path() -> Path:
    """Resolves the default SQLite database path in tempfile.gettempdir(),
    falling back to the project folder only if that fails.
    """
    try:
        temp_dir = Path(tempfile.gettempdir())
        temp_dir.mkdir(parents=True, exist_ok=True)
        db_path = temp_dir / "parkvision.db"
        probe = temp_dir / f".pv_probe_{os.getpid()}"
        probe.touch(exist_ok=True)
        probe.unlink(missing_ok=True)
        return db_path
    except Exception:
        return Path("parkvision.db")


def get_db_path() -> Path:
    """Returns the shared SQLite database file path.
    Located in tempfile.gettempdir(), falling back to the project folder only if that fails.
    Respects DB_PATH when overridden (e.g. via monkeypatch in unit tests).
    """
    global _SHARED_DB_PATH, DB_PATH
    if "DB_PATH" in globals() and DB_PATH is not None:
        if _SHARED_DB_PATH is not None and Path(DB_PATH) != Path(_SHARED_DB_PATH):
            return Path(DB_PATH)
    if _SHARED_DB_PATH is None:
        _SHARED_DB_PATH = _resolve_default_db_path()
    return _SHARED_DB_PATH


_SHARED_DB_PATH = _resolve_default_db_path()
DB_PATH = _SHARED_DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled.
    Every connection uses timeout=30.
    """
    conn = sqlite3.connect(get_db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> bool:
    """Initializes tables, migrates missing columns, and seeds default accounts.
    Uses module-level threading.Lock, single connection with BEGIN IMMEDIATE ... COMMIT,
    and handles retries and corruption recovery safely.
    """
    from auth.security import hash_password

    with _db_lock:
        db_path = get_db_path()
        max_retries = 5

        for attempt in range(max_retries + 1):
            try:
                conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
                try:
                    cursor = conn.cursor()
                    cursor.execute("BEGIN IMMEDIATE")
                    try:
                        # Users table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                full_name TEXT NOT NULL,
                                email TEXT UNIQUE NOT NULL,
                                password_hash TEXT NOT NULL,
                                salt TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)

                        # Analysis history table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS analyses (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                user_email TEXT,
                                image_name TEXT NOT NULL,
                                total_slots INTEGER NOT NULL,
                                occupied_slots INTEGER NOT NULL,
                                available_slots INTEGER NOT NULL,
                                occupancy_pct REAL NOT NULL,
                                congestion TEXT NOT NULL,
                                recommendation TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                            )
                        """)

                        # User feedback table
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS feedback (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                user_email TEXT,
                                rating INTEGER NOT NULL,
                                prediction_correct TEXT NOT NULL,
                                wrong_slots TEXT,
                                comments TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)

                        # Migration: Ensure user_email column exists on analyses
                        cursor.execute("PRAGMA table_info(analyses)")
                        analyses_cols = [r[1] for r in cursor.fetchall()]
                        if "user_email" not in analyses_cols:
                            cursor.execute("ALTER TABLE analyses ADD COLUMN user_email TEXT")
                            # Migrate old unassigned rows only when column was just added.
                            # Never move Guest data into demo account.
                            cursor.execute(
                                "UPDATE analyses SET user_email = 'demo@parkvision.ai', user_id = 1 WHERE user_email IS NULL OR user_email = ''"
                            )

                        # Migration: Ensure user_email column exists on feedback
                        cursor.execute("PRAGMA table_info(feedback)")
                        feedback_cols = [r[1] for r in cursor.fetchall()]
                        if "user_email" not in feedback_cols:
                            cursor.execute("ALTER TABLE feedback ADD COLUMN user_email TEXT")
                            cursor.execute(
                                "UPDATE feedback SET user_email = 'demo@parkvision.ai', user_id = 1 WHERE user_email IS NULL OR user_email = ''"
                            )

                        # Seed demo account if not present using INSERT OR IGNORE
                        p_hash, salt = hash_password("Demo@1234")
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO users (full_name, email, password_hash, salt)
                            VALUES (?, ?, ?, ?)
                            """,
                            ("Demo Analyst", "demo@parkvision.ai", p_hash, salt),
                        )

                        cursor.execute("COMMIT")
                        return True
                    except Exception:
                        try:
                            cursor.execute("ROLLBACK")
                        except Exception:
                            pass
                        raise
                finally:
                    conn.close()

            except sqlite3.IntegrityError as e:
                # Do NOT delete the database file for an IntegrityError
                logging.error(f"Database IntegrityError during init_db: {e}")
                return False

            except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                err_msg = str(e).lower()
                # Delete and recreate only if the file is damaged ("file is not a database" or "malformed")
                if "file is not a database" in err_msg or "malformed" in err_msg:
                    logging.warning(f"Database file is damaged ({e}). Deleting and recreating.")
                    try:
                        if db_path.exists():
                            db_path.unlink()
                        for extra in (str(db_path) + "-wal", str(db_path) + "-shm", str(db_path) + "-journal"):
                            extra_path = Path(extra)
                            if extra_path.exists():
                                extra_path.unlink()
                    except Exception as del_err:
                        logging.error(f"Failed to delete corrupted database: {del_err}")
                    if attempt < max_retries:
                        continue
                    return False

                # If init_db() hits "database is locked", wait 1 second and retry, up to 5 times
                if "locked" in err_msg or "busy" in err_msg:
                    logging.warning(f"Database locked on attempt {attempt + 1}. Retrying in 1s...")
                    if attempt < max_retries:
                        time.sleep(1)
                        continue
                    else:
                        logging.error("Database locked after maximum retries.")
                        return False

                logging.error(f"Database error during init_db: {e}")
                return False

            except Exception as e:
                logging.error(f"Unexpected error during init_db: {e}")
                return False

        return False


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user dictionary by case-insensitive email."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, full_name, email, password_hash, salt, created_at FROM users WHERE lower(email) = lower(?)",
            (email.strip(),),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    except Exception:
        return None


def create_user(full_name: str, email: str, password_hash: str, salt: str) -> int:
    """Inserts a new user and returns their user ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
        (full_name.strip(), email.strip().lower(), password_hash, salt),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def save_analysis(
    user_id: Optional[int],
    user_email: Optional[str],
    image_name: str,
    total_slots: int,
    occupied_slots: int,
    available_slots: int,
    occupancy_pct: float,
    congestion: str,
    recommendation: str = "",
) -> int:
    """Saves a completed parking lot inference run to SQLite history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO analyses 
        (user_id, user_email, image_name, total_slots, occupied_slots, available_slots, occupancy_pct, congestion, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            user_email.strip().lower() if user_email else None,
            image_name,
            total_slots,
            occupied_slots,
            available_slots,
            occupancy_pct,
            congestion,
            recommendation,
        ),
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_user_analyses(user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetches analysis history for a specific user ID ordered by latest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, user_email, image_name, total_slots, occupied_slots, available_slots, occupancy_pct, congestion, recommendation, created_at
        FROM analyses
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_analyses_by_email(user_email: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetches analysis history strictly for a specific user email ordered by latest first."""
    if not user_email:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, user_email, image_name, total_slots, occupied_slots, available_slots, occupancy_pct, congestion, recommendation, created_at
        FROM analyses
        WHERE lower(user_email) = lower(?)
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_email.strip(), limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_analyses(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetches all analysis history ordered by latest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, user_email, image_name, total_slots, occupied_slots, available_slots, occupancy_pct, congestion, recommendation, created_at
        FROM analyses
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_feedback(
    user_id: Optional[int],
    user_email: Optional[str],
    rating: int,
    prediction_correct: str,
    wrong_slots: str,
    comments: str,
) -> int:
    """Saves user feedback to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO feedback (user_id, user_email, rating, prediction_correct, wrong_slots, comments)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            user_email.strip().lower() if user_email else None,
            rating,
            prediction_correct,
            wrong_slots,
            comments,
        ),
    )
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return feedback_id


def get_user_feedback_by_email(user_email: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Returns recent feedback submissions strictly for a specific user email."""
    if not user_email:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, user_email, rating, prediction_correct, wrong_slots, comments, created_at
        FROM feedback
        WHERE lower(user_email) = lower(?)
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_email.strip(), limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_feedback_records(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns recent feedback submissions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, user_email, rating, prediction_correct, wrong_slots, comments, created_at
        FROM feedback
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
