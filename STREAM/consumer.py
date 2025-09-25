from kafka import KafkaConsumer
import json, psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="campus_safety",
    user="postgres",
    password="Mahlatsi#0310",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create tables from schema
with open("schema.sql", "r", encoding="utf-8") as f:
    cursor.execute(f.read())
conn.commit()

# Insert queries
queries = {
    "safety-reports-topic": (
        "INSERT INTO safety_reports (reporter, category, description, lat, lon, timestamp) VALUES (%s,%s,%s,%s,%s,%s)",
        ["reporter","category","description","lat","lon","timestamp"]
    ),
    "routes-topic": (
        "INSERT INTO safe_routes (origin,destination,risk_score,timestamp) VALUES (%s,%s,%s,%s)",
        ["origin","destination","risk_score","timestamp"]
    ),
    "loadshedding-topic": (
        "INSERT INTO loadshedding (area,stage,start_time,end_time) VALUES (%s,%s,%s,%s)",
        ["area","stage","start_time","end_time"]
    ),
    "green-areas-topic": (
        "INSERT INTO green_areas (name, lat, lon, radius_m) VALUES (%s,%s,%s,%s)",
        ["name","lat","lon","radius_m"]
    )
}

# Kafka consumer
consumer = KafkaConsumer(
    *queries.keys(),
    bootstrap_servers='localhost:29092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consuming from all topics...")

try:
    for msg in consumer:
        topic = msg.topic
        data = msg.value
        insert_query, fields = queries[topic]
        try:
            cursor.execute(insert_query, tuple(data[f] for f in fields))
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