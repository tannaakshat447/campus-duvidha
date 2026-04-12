"""
Database models — CRUD helpers for every table.
Each function opens its own connection so callers never worry about lifecycle.
"""

import json
import datetime
from typing import Optional, List, Dict, Any

from database.db import get_connection


# ════════════════════════════════════════════════════════════════════════════
#  USERS
# ════════════════════════════════════════════════════════════════════════════

def create_user(email: str, password_hash: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash),
        )
        row_id = cur.lastrowid
        conn.commit()
    except Exception as e:
        conn.close()
        raise e
    conn.close()
    return row_id

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

# ════════════════════════════════════════════════════════════════════════════
#  PROBLEMS
# ════════════════════════════════════════════════════════════════════════════

def insert_problem(
    description: str,
    tracking_id: str,
    student_name: str = "Anonymous",
    student_email: Optional[str] = None,
    image_blob: Optional[bytes] = None,
    category: str = "",
    confidence: float = 0.0,
    priority: str = "",
    priority_reason: str = "",
    summary: str = "",
    department: str = "",
    routing_reason: str = "",
    sentiment: str = "",
    flagged: bool = False,
    status: str = "Submitted",
    used_fallback: bool = False,
) -> int:
    """Insert a new problem and return its row id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO problems
           (description, tracking_id, student_name, student_email, image_blob,
            category, confidence, priority, priority_reason,
            summary, department, routing_reason, sentiment,
            flagged, status, used_fallback)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            description, tracking_id, student_name, student_email, image_blob,
            category, confidence, priority, priority_reason,
            summary, department, routing_reason, sentiment,
            int(flagged), status, int(used_fallback),
        ),
    )
    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id


def get_problems_by_email(email: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM problems WHERE student_email = ? ORDER BY created_at DESC", (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_problem_by_tracking_id(tracking_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM problems WHERE tracking_id = ?", (tracking_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_problem_by_id(problem_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM problems WHERE id = ?", (problem_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_problems(
    department: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    flagged_only: bool = False,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Fetch problems with optional filters and pagination."""
    conn = get_connection()
    query = "SELECT * FROM problems WHERE 1=1"
    params: list = []

    if department:
        query += " AND department = ?"
        params.append(department)
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if flagged_only:
        query += " AND flagged = 1"

    query += " ORDER BY created_at DESC"
    
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    if offset is not None:
        query += " OFFSET ?"
        params.append(offset)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_problem_status(problem_id: int, new_status: str, changed_by: str = "Admin"):
    conn = get_connection()
    old_row = conn.execute(
        "SELECT status FROM problems WHERE id = ?", (problem_id,)
    ).fetchone()
    old_status = dict(old_row)["status"] if old_row else "Unknown"

    conn.execute(
        "UPDATE problems SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, problem_id),
    )
    conn.execute(
        "INSERT INTO status_logs (problem_id, old_status, new_status, changed_by) VALUES (?,?,?,?)",
        (problem_id, old_status, new_status, changed_by),
    )
    conn.commit()
    conn.close()


def update_problem_fields(problem_id: int, **kwargs):
    """Generic updater — pass column=value pairs."""
    if not kwargs:
        return
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values())
    vals.append(problem_id)
    conn.execute(f"UPDATE problems SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", vals)
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════════════════════
#  STATUS LOGS
# ════════════════════════════════════════════════════════════════════════════

def insert_status_log(problem_id: int, old_status: str, new_status: str, changed_by: str = "System"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO status_logs (problem_id, old_status, new_status, changed_by) VALUES (?,?,?,?)",
        (problem_id, old_status, new_status, changed_by),
    )
    conn.commit()
    conn.close()


def get_status_logs(problem_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM status_logs WHERE problem_id = ? ORDER BY changed_at ASC",
        (problem_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════════════════════
#  COMMENTS
# ════════════════════════════════════════════════════════════════════════════

def insert_comment(problem_id: int, comment: str, posted_by: str = "Admin"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO comments (problem_id, comment, posted_by) VALUES (?,?,?)",
        (problem_id, comment, posted_by),
    )
    conn.commit()
    conn.close()


def get_comments(problem_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM comments WHERE problem_id = ? ORDER BY posted_at ASC",
        (problem_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════════════════════
#  AGENT LOGS
# ════════════════════════════════════════════════════════════════════════════

def insert_agent_log(problem_id: int, agent_name: str, input_text: str, output_json: str, latency_ms: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO agent_logs (problem_id, agent_name, input_text, output_json, latency_ms) VALUES (?,?,?,?,?)",
        (problem_id, agent_name, input_text, output_json, latency_ms),
    )
    conn.commit()
    conn.close()


def get_agent_logs(problem_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM agent_logs WHERE problem_id = ? ORDER BY created_at ASC",
        (problem_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_agent_logs() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM agent_logs ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════════════════════
#  ANALYTICS HELPERS
# ════════════════════════════════════════════════════════════════════════════

def get_category_distribution() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) as count FROM problems GROUP BY category ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_priority_distribution() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT priority, COUNT(*) as count FROM problems GROUP BY priority ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sentiment_distribution() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT sentiment, COUNT(*) as count FROM problems GROUP BY sentiment ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_department_stats() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT department,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
               AVG(CASE WHEN status = 'Resolved'
                   THEN (julianday(updated_at) - julianday(created_at)) * 24
                   ELSE NULL END) as avg_resolution_hours
        FROM problems
        GROUP BY department
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_submissions(days: int = 7) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute(f"""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM problems
        WHERE created_at >= datetime('now', '-{days} days')
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_flagged_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as c FROM problems WHERE flagged = 1").fetchone()
    conn.close()
    return dict(row)["c"]


def get_avg_confidence() -> float:
    conn = get_connection()
    row = conn.execute("SELECT AVG(confidence) as avg_conf FROM problems WHERE confidence > 0").fetchone()
    conn.close()
    val = dict(row)["avg_conf"]
    return val if val else 0.0


def get_fallback_rate() -> float:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()
    fallbacks = conn.execute("SELECT COUNT(*) as c FROM problems WHERE used_fallback = 1").fetchone()
    conn.close()
    t = dict(total)["c"]
    f = dict(fallbacks)["c"]
    return (f / t * 100) if t > 0 else 0.0


def get_total_problems() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()
    conn.close()
    return dict(row)["c"]
