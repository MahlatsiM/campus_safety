import os
import json
from kafka import KafkaConsumer
import psycopg2
from datetime import datetime

# Kafka settings
KAFKA_BROKER = 'kafka:9092'
TOPICS = ['safety-reports-topic', 'routes-topic', 'loadshedding-topic']

# PostgreSQL connection
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgres://postgres:Mahlatsi%230310@postgres:5432/campus_safety'
)
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Kafka consumer
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m)
)

print("Consumer started, listening to topics:", TOPICS)

for message in consumer:
    topic = message.topic
    data = message.value

    if topic == 'safety-reports-topic':
        cursor.execute(
            """
            INSERT INTO safety_reports (reporter, category, description, lat, lon, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data.get('reporter'),
                data.get('category'),
                data.get('description'),
                data.get('lat'),
                data.get('lon'),
                datetime.fromisoformat(data.get('timestamp'))
            )
        )
    elif topic == 'routes-topic':
        cursor.execute(
            """
            INSERT INTO safe_routes (origin, destination, risk_score, timestamp)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data.get('origin'),
                data.get('destination'),
                data.get('risk_score'),
                datetime.fromisoformat(data.get('timestamp'))
            )
        )
    elif topic == 'loadshedding-topic':
        cursor.execute(
            """
            INSERT INTO loadshedding (area, stage, start_time, end_time)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data.get('area'),
                data.get('stage'),
                datetime.fromisoformat(data.get('start_time')),
                datetime.fromisoformat(data.get('end_time'))
            )
        )
    conn.commit()
    print(f"Inserted data from topic {topic}: {data}")
