import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import DATABASE_PATH, SUSTAINED_PRESENCE_SECONDS

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        class_name TEXT NOT NULL,
        instructor TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        duration_minutes INTEGER DEFAULT 0,
        avg_engagement REAL DEFAULT 0.0,
        total_students INTEGER DEFAULT 0,
        present_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Active'
    )
    """)

    # Students registry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        email TEXT,
        avatar_color TEXT DEFAULT '#4f46e5'
    )
    """)

    # Attendance logs (sustained presence records)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        sustained_seconds REAL DEFAULT 0.0,
        confidence REAL DEFAULT 0.0,
        status TEXT DEFAULT 'Absent',
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        UNIQUE(session_id, student_id)
    )
    """)

    # Multimodal Engagement timeline logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engagement_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        elapsed_seconds INTEGER NOT NULL,
        overall_score REAL NOT NULL,
        visual_attention REAL NOT NULL,
        vocal_activity REAL NOT NULL,
        active_faces_count INTEGER NOT NULL,
        head_pitch REAL DEFAULT 0.0,
        head_yaw REAL DEFAULT 0.0,
        alert_flag TEXT DEFAULT 'Normal',
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
    """)

    # AI Teaching Suggestions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teaching_suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        elapsed_seconds INTEGER NOT NULL,
        trigger_reason TEXT NOT NULL,
        category TEXT NOT NULL,
        suggestion_text TEXT NOT NULL,
        action_item TEXT NOT NULL,
        applied INTEGER DEFAULT 0,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
    """)

    conn.commit()

    # Seed initial students if table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        default_students = [
            ("s_101", "Aarav Sharma", "CS-2026-001", "Computer Science", "aarav.sharma@univ.edu", "#3b82f6"),
            ("s_102", "Priya Patel", "CS-2026-002", "Computer Science", "priya.patel@univ.edu", "#ec4899"),
            ("s_103", "Rohan Verma", "CS-2026-003", "Data Science", "rohan.verma@univ.edu", "#10b981"),
            ("s_104", "Ananya Iyer", "CS-2026-004", "Artificial Intelligence", "ananya.iyer@univ.edu", "#f59e0b"),
            ("s_105", "Kabir Singh", "CS-2026-005", "Computer Science", "kabir.singh@univ.edu", "#8b5cf6"),
            ("s_106", "Diya Mukherjee", "CS-2026-006", "Artificial Intelligence", "diya.m@univ.edu", "#06b6d4"),
            ("s_107", "Manish Kumar", "CS-2026-007", "Machine Learning", "manishkr8028@gmail.com", "#6366f1"),
            ("s_108", "Sneha Reddy", "CS-2026-008", "Data Science", "sneha.reddy@univ.edu", "#14b8a6"),
        ]
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", default_students)
        conn.commit()

    # Seed a demo benchmark session if none exist
    cursor.execute("SELECT COUNT(*) FROM sessions")
    if cursor.fetchone()[0] == 0:
        seed_demo_session(cursor)
        conn.commit()

    conn.close()

def seed_demo_session(cursor):
    session_id = "sess_demo_2026"
    start_dt = datetime.now() - timedelta(minutes=45)
    end_dt = datetime.now()
    
    cursor.execute("""
    INSERT INTO sessions (id, title, class_name, instructor, start_time, end_time, duration_minutes, avg_engagement, total_students, present_count, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        "Generative AI & Multimodal Intelligence Lab",
        "CS-401: Advanced AI Architectures",
        "Prof. S. R. Ramanujan",
        start_dt.isoformat(),
        end_dt.isoformat(),
        45,
        78.4,
        8,
        7,
        "Completed"
    ))

    # Seed attendance logs
    cursor.execute("SELECT id FROM students")
    students = [row[0] for row in cursor.fetchall()]
    
    for i, s_id in enumerate(students):
        # Student 105 absent for realistic variance
        if s_id == "s_105":
            status = "Absent"
            sustained = 4.0
        elif s_id == "s_104":
            status = "Late"
            sustained = 28.0
        else:
            status = "Present"
            sustained = 42.0

        cursor.execute("""
        INSERT INTO attendance_logs (session_id, student_id, first_seen, last_seen, sustained_seconds, confidence, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            s_id,
            (start_dt + timedelta(minutes=2 if status != 'Late' else 15)).isoformat(),
            end_dt.isoformat(),
            sustained * 60,
            0.94 if status == "Present" else 0.82,
            status
        ))

    # Seed engagement timeline data (45 data points)
    base_scores = [72, 75, 78, 82, 85, 84, 88, 89, 91, 90, 86, 82, 79, 74, 69, 65, 62, 59, 68, 74, 80, 83, 86, 88, 87, 85, 82, 80, 78, 75, 73, 71, 76, 82, 85, 87, 89, 90, 88, 84, 82, 79, 77, 75, 74]
    for m, score in enumerate(base_scores):
        t = start_dt + timedelta(minutes=m)
        vocal = min(100.0, max(10.0, score * 0.85 + (m % 5) * 4))
        visual = min(100.0, max(20.0, score * 0.95 - (m % 4) * 3))
        alert = "Attention Drop" if score < 65 else ("Active Discussion" if vocal > 80 else "Normal")
        
        cursor.execute("""
        INSERT INTO engagement_logs (session_id, timestamp, elapsed_seconds, overall_score, visual_attention, vocal_activity, active_faces_count, head_pitch, head_yaw, alert_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            t.isoformat(),
            m * 60,
            float(score),
            float(visual),
            float(vocal),
            7 if m > 14 else 6,
            -2.1 if score < 70 else 0.5,
            3.2 if score < 70 else 0.2,
            alert
        ))

    # Seed teaching suggestions
    suggestions = [
        (
            16 * 60,
            "Sustained visual attention dropped below 65% for 3+ minutes",
            "Pacing & Interactivity",
            "Learner gaze drift detected across the central cluster. Consider introducing an interactive concept-check question or Quick Poll.",
            "Launch a 60-second live quiz on today's core architecture diagram."
        ),
        (
            28 * 60,
            "Low vocal participation and prolonged teacher monologue",
            "Discussion Prompt",
            "Vocal activity has been predominantly unidirectional for 12 minutes. Encourage peer-to-peer breakout or solicit student reactions.",
            "Ask student in row 2 (Priya / Rohan) to summarize the trade-offs of offline edge computing."
        ),
        (
            38 * 60,
            "High engagement peak detected following practical code demo",
            "Positive Reinforcement",
            "Multimodal engagement surged to 90%+ during hands-on model walkthrough. Students are highly responsive to visual architecture slides.",
            "Consolidate current momentum by assigning the next coding step as a pair activity."
        )
    ]

    for elapsed, trigger, cat, sug, act in suggestions:
        cursor.execute("""
        INSERT INTO teaching_suggestions (session_id, timestamp, elapsed_seconds, trigger_reason, category, suggestion_text, action_item, applied)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            session_id,
            (start_dt + timedelta(seconds=elapsed)).isoformat(),
            elapsed,
            trigger,
            cat,
            sug,
            act
        ))

# Session CRUD operations
def create_session(session_id: str, title: str, class_name: str, instructor: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO sessions (id, title, class_name, instructor, start_time, status)
    VALUES (?, ?, ?, ?, ?, 'Active')
    """, (session_id, title, class_name, instructor, now_str))
    conn.commit()
    conn.close()
    return {"id": session_id, "title": title, "class_name": class_name, "start_time": now_str, "status": "Active"}

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def list_sessions(limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_session_summary(session_id: str, avg_engagement: float, present_count: float, total_students: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
    UPDATE sessions
    SET avg_engagement = ?, present_count = ?, total_students = ?, end_time = ?, status = 'Completed'
    WHERE id = ?
    """, (avg_engagement, present_count, total_students, now_str, session_id))
    conn.commit()
    conn.close()

# Attendance operations
def record_presence(session_id: str, student_id: str, confidence: float = 0.95):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    cursor.execute("SELECT first_seen, sustained_seconds FROM attendance_logs WHERE session_id = ? AND student_id = ?", (session_id, student_id))
    row = cursor.fetchone()

    if row:
        new_sustained = row['sustained_seconds'] + 2.0  # approximate 2-sec sampling interval
        status = 'Present' if new_sustained >= SUSTAINED_PRESENCE_SECONDS else 'Evaluating'
        cursor.execute("""
        UPDATE attendance_logs
        SET last_seen = ?, sustained_seconds = ?, status = ?, confidence = ?
        WHERE session_id = ? AND student_id = ?
        """, (now_str, new_sustained, status, confidence, session_id, student_id))
    else:
        cursor.execute("""
        INSERT INTO attendance_logs (session_id, student_id, first_seen, last_seen, sustained_seconds, confidence, status)
        VALUES (?, ?, ?, ?, 2.0, ?, 'Evaluating')
        """, (session_id, student_id, now_str, now_str, confidence))

    conn.commit()
    conn.close()

def get_session_attendance(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.id, s.name, s.roll_no, s.department, s.avatar_color,
           COALESCE(a.status, 'Absent') as attendance_status,
           COALESCE(a.sustained_seconds, 0) as sustained_seconds,
           COALESCE(a.confidence, 0.0) as confidence,
           a.first_seen, a.last_seen
    FROM students s
    LEFT JOIN attendance_logs a ON s.id = a.student_id AND a.session_id = ?
    ORDER BY s.roll_no ASC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Engagement Logs operations
def log_engagement(session_id: str, elapsed_seconds: int, score: float, visual: float, vocal: float, faces: int, pitch: float, yaw: float, alert: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO engagement_logs (session_id, timestamp, elapsed_seconds, overall_score, visual_attention, vocal_activity, active_faces_count, head_pitch, head_yaw, alert_flag)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, now_str, elapsed_seconds, score, visual, vocal, faces, pitch, yaw, alert))
    conn.commit()
    conn.close()

def get_engagement_timeline(session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT elapsed_seconds, overall_score, visual_attention, vocal_activity, active_faces_count, head_pitch, head_yaw, alert_flag, timestamp
    FROM engagement_logs
    WHERE session_id = ?
    ORDER BY elapsed_seconds ASC
    LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# AI Teaching Suggestions operations
def add_teaching_suggestion(session_id: str, elapsed_seconds: int, trigger: str, category: str, suggestion: str, action: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO teaching_suggestions (session_id, timestamp, elapsed_seconds, trigger_reason, category, suggestion_text, action_item)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, now_str, elapsed_seconds, trigger, category, suggestion, action))
    conn.commit()
    conn.close()

def get_teaching_suggestions(session_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM teaching_suggestions
    WHERE session_id = ?
    ORDER BY elapsed_seconds DESC
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
