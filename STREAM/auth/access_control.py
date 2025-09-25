# auth/access_control.py
from datetime import datetime, timedelta
import psycopg2

# Connect to DB
conn = psycopg2.connect(
    dbname="campus_safety",
    user="postgres",
    password="Mahlatsi#0310",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Table to track blocked users
cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_users (
    username TEXT PRIMARY KEY,
    blocked_until TIMESTAMP
)
""")
conn.commit()

def block_user(username: str, duration_seconds: int = 600):  # default 10 minutes
    blocked_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
    try:
        cursor.execute("""
        INSERT INTO blocked_users (username, blocked_until)
        VALUES (%s, %s)
        ON CONFLICT (username) DO UPDATE SET blocked_until=%s
        """, (username, blocked_until, blocked_until))
        conn.commit()
        print(f"User {username} blocked until {blocked_until}")
    except Exception as e:
        conn.rollback()
        print(f"Failed to block user: {e}")

def is_user_blocked(username: str) -> bool:
    cursor.execute("SELECT blocked_until FROM blocked_users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if row:
        blocked_until = row[0]
        if blocked_until > datetime.utcnow():
            return True
        else:
            # unblock user automatically
            cursor.execute("DELETE FROM blocked_users WHERE username=%s", (username,))
            conn.commit()
            return False
    return False
