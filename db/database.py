"""
Database persistence module for ParkVision AI.
Uses Python standard library sqlite3.
Handles users, analysis history, and user feedback.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = Path("parkvision.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes tables, migrates missing columns, and seeds default accounts."""
    from auth.security import hash_password

    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.commit()

    # Migration: Ensure user_email column exists on analyses
    cursor.execute("PRAGMA table_info(analyses)")
    analyses_cols = [r[1] for r in cursor.fetchall()]
    if "user_email" not in analyses_cols:
        cursor.execute("ALTER TABLE analyses ADD COLUMN user_email TEXT")
        conn.commit()

    # Migrate old unassigned or guest rows to demo account
    cursor.execute(
        "UPDATE analyses SET user_email = 'demo@parkvision.ai', user_id = 1 WHERE user_email IS NULL OR user_email = '' OR lower(user_email) = 'guest@parkvision.ai'"
    )
    cursor.execute(
        "UPDATE feedback SET user_email = 'demo@parkvision.ai', user_id = 1 WHERE user_email IS NULL OR user_email = '' OR lower(user_email) = 'guest@parkvision.ai'"
    )
    conn.commit()

    # Seed demo account if not present
    cursor.execute("SELECT id FROM users WHERE lower(email) = ?", ("demo@parkvision.ai",))
    if cursor.fetchone() is None:
        p_hash, salt = hash_password("Demo@1234")
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            ("Demo Analyst", "demo@parkvision.ai", p_hash, salt),
        )
        conn.commit()

    # Seed / ensure Tanmay account
    cursor.execute("SELECT id FROM users WHERE lower(email) = ?", ("tanmay@parkvision.ai",))
    tanmay_row = cursor.fetchone()
    p_hash_t, salt_t = hash_password("Tanmay@1234")
    if tanmay_row is None:
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            ("Tanmay", "tanmay@parkvision.ai", p_hash_t, salt_t),
        )
        conn.commit()
    else:
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ?, full_name = ? WHERE lower(email) = ?",
            (p_hash_t, salt_t, "Tanmay", "tanmay@parkvision.ai"),
        )
        conn.commit()

    conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user dictionary by case-insensitive email."""
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

