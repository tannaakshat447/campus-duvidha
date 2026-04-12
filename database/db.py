"""
Database connection helper — SQLite via sqlite3.
Provides a context-manager for safe transactions and an init function
that creates all tables on first run.
"""

import sqlite3
import os
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row-factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        email           TEXT    UNIQUE NOT NULL,
        password_hash   TEXT    NOT NULL,
        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS problems (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        description     TEXT    NOT NULL,
        image_blob      BLOB,
        category        TEXT,
        confidence      REAL,
        priority        TEXT,
        priority_reason TEXT,
        summary         TEXT,
        department      TEXT,
        routing_reason  TEXT,
        sentiment       TEXT,
        flagged         INTEGER DEFAULT 0,
        status          TEXT    DEFAULT 'Submitted',
        used_fallback   INTEGER DEFAULT 0,
        tracking_id     TEXT    UNIQUE,
        student_name    TEXT    DEFAULT 'Anonymous',
        student_email   TEXT    DEFAULT NULL,
        created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS status_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id  INTEGER NOT NULL,
        old_status  TEXT,
        new_status  TEXT    NOT NULL,
        changed_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        changed_by  TEXT    DEFAULT 'System',
        FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS comments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id  INTEGER NOT NULL,
        comment     TEXT    NOT NULL,
        posted_by   TEXT    DEFAULT 'Admin',
        posted_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS agent_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id  INTEGER NOT NULL,
        agent_name  TEXT    NOT NULL,
        input_text  TEXT,
        output_json TEXT,
        latency_ms  REAL,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
