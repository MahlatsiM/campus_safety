# auth/auth.py
import psycopg2
from datetime import datetime
import bcrypt

# Connect to DB for setup
conn = psycopg2.connect(
    dbname="campus_safety",
    user="postgres",
    password="Mahlatsi#0310",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    last_login TIMESTAMP
)
""")
conn.commit()

def register_user(username, password):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="campus_safety",
            user="postgres",
            password="Mahlatsi#0310"
        )
        cur = conn.cursor()

        # Check if username exists
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return False, "Username already exists"

        # Hash password and store as UTF-8 string
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        cur.close()
        conn.close()
        return True, f"User {username} registered successfully"

    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def authenticate(username: str, password: str) -> bool:
    cursor.execute("SELECT password_hash FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if row:
        stored_hash = row[0].encode('utf-8')  # Ensure bytes
        if bcrypt.checkpw(password.encode(), stored_hash):
            cursor.execute("UPDATE users SET last_login=%s WHERE username=%s", (datetime.utcnow(), username))
            conn.commit()
            return True
    return False
