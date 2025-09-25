from kafka import KafkaConsumer
import json, psycopg2

conn = psycopg2.connect(
    dbname="campus_safety",
    user="postgres",
    password="Mahlatsi#0310",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create tables
cursor.execute(open("schema.sql", "r").read())
conn.commit()

# Define queries and fields
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
    )
}

# Subscribe to all topics at once
consumer = KafkaConsumer(
    *queries.keys(),  # subscribe to all topics
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
        cursor.execute(insert_query, tuple(data[f] for f in fields))
        conn.commit()
        print(f"Inserted into {topic}: {data}")

except KeyboardInterrupt:
    print("Consumer stopped.")
finally:
    cursor.close()
    conn.close()