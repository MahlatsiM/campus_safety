from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="campus_safety",
    user="postgres",
    password="Mahlatsi#0310",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create tables from schema if needed
with open("schema.sql", "r", encoding="utf-8") as f:
    cursor.execute(f.read())
conn.commit()

# Mapping topics to insert statements and fields
queries = {
    "users-topic": (
        "INSERT INTO users (user_id, session_cookie, created_at, last_seen) "
        "VALUES (%s,%s,%s,%s) "
        "ON CONFLICT (user_id) DO UPDATE SET "
        "session_cookie = EXCLUDED.session_cookie, last_seen = EXCLUDED.last_seen",
        ["user_id", "session_cookie", "created_at", "last_seen"]
    ),
    "safety-reports-topic": (
        "INSERT INTO safety_reports (user_id, report_type, description, latitude, longitude, created_at) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        ["user_id","report_type","description","latitude","longitude","created_at"]
    )
}

# Kafka consumer
consumer = KafkaConsumer(
    *queries.keys(),
    bootstrap_servers='localhost:29092',  # match producer
    group_id="campus_safety_consumer",
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consuming from topics:", list(queries.keys()))

try:
    for msg in consumer:
        topic = msg.topic
        data = msg.value
        print(f"Received from Kafka [{topic}]: {data}")  # debug

        insert_query, fields = queries[topic]
        try:
            row_values = []
            for f in fields:
                val = data.get(f)
                if isinstance(val, str) and f in ("created_at", "last_seen"):
                    val = datetime.fromisoformat(val)
                row_values.append(val)

            cursor.execute(insert_query, tuple(row_values))
            conn.commit()
            print(f"Inserted into {topic}: {data}")
        except Exception as e:
            conn.rollback()
            print(f"Failed to insert into {topic}: {e}, data: {data}")

except KeyboardInterrupt:
    print("Consumer stopped.")
finally:
    cursor.close()
    conn.close()
