import sqlite3
import datetime
from config import DB_NAME

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            phone TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Shikoyat va murojaatlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            username TEXT,
            phone TEXT,
            department TEXT,
            reason TEXT,
            details TEXT,
            student_id TEXT,
            status TEXT DEFAULT 'Yangi',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Eskiroq bazalar uchun ustun tekshiruvi
    cursor.execute("PRAGMA table_info(complaints)")
    columns = [col[1] for col in cursor.fetchall()]
    if "student_id" not in columns:
        cursor.execute("ALTER TABLE complaints ADD COLUMN student_id TEXT")
    
    conn.commit()
    conn.close()

def save_user(user_id: int, full_name: str, username: str = None, phone: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, full_name, username, phone)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name = excluded.full_name,
            username = excluded.username,
            phone = COALESCE(excluded.phone, users.phone)
    """, (user_id, full_name, username, phone))
    conn.commit()
    conn.close()

def add_complaint(user_id: int, full_name: str, username: str, phone: str, 
                  department: str, reason: str, details: str, student_id: str = "Noma'lum") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (user_id, full_name, username, phone, department, reason, details, student_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, full_name, username, phone, department, reason, details, student_id))
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return complaint_id

def get_complaint(complaint_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_recent_complaints(limit: int = 10, status: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM complaints WHERE status = ? ORDER BY id DESC LIMIT ?", (status, limit))
    else:
        cursor.execute("SELECT * FROM complaints ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_status(complaint_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
    conn.commit()
    conn.close()

def get_statistics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Yangi'")
    new_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Ko‘rib chiqilmoqda'")
    in_review = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Hal etildi'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
    total_users = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total": total,
        "new": new_count,
        "in_review": in_review,
        "resolved": resolved,
        "total_users": total_users
    }
