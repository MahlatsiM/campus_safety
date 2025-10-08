# prerequisites: pip install passlib psycopg2-binary
from passlib.hash import pbkdf2_sha256
import psycopg2

pw = "Mahla#03"
hashed = pbkdf2_sha256.hash(pw)

conn = psycopg2.connect(
    host="localhost",
    dbname="campus_safety",
    user="postgres",
    password="Mahlatsi#0310",
    port="5432"
)
cur = conn.cursor()
cur.execute("""
    INSERT INTO users (username, email, first_name, last_name, hashed_password, is_admin, created_at)
    VALUES (%s,%s,%s,%s,%s,%s,NOW())
""", ('mahlatsi', 'admin@campussafety.local', 'Mahlatsi', 'Mashilo', hashed, True))
conn.commit()
cur.close()
conn.close()
print("Admin created.")