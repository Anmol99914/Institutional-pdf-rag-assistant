import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "processed", "feedback.db")


def init_db():
    """Creates the database and tables if they don't already exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            top_score REAL,
            low_confidence INTEGER NOT NULL,
            feedback TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_interaction(question, answer, sources, low_confidence):
    """
    Logs every Q&A interaction. Returns the interaction's row id,
    so feedback can later be attached to it.
    """
    top_score = sources[0]["score"] if sources else None
    sources_str = "; ".join(f"{s['source']} p{s['page']} ({s['score']})" for s in sources)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interactions (timestamp, question, answer, sources, top_score, low_confidence, feedback)
        VALUES (?, ?, ?, ?, ?, ?, NULL)
    """, (
        datetime.now().isoformat(),
        question,
        answer,
        sources_str,
        top_score,
        1 if low_confidence else 0
    ))
    conn.commit()
    interaction_id = cursor.lastrowid
    conn.close()
    return interaction_id


def record_feedback(interaction_id, feedback_value):
    """feedback_value should be 'helpful' or 'not_helpful'."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE interactions SET feedback = ? WHERE id = ?", (feedback_value, interaction_id))
    conn.commit()
    conn.close()


def get_low_confidence_or_negative(limit=50):
    """Returns rows that were low-confidence OR received negative feedback — useful for Phase 11 evaluation review."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, question, answer, top_score, low_confidence, feedback
        FROM interactions
        WHERE low_confidence = 1 OR feedback = 'not_helpful'
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows