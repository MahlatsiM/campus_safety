# consumer.py
import os
import json
import time
from kafka import KafkaConsumer, errors
import psycopg2
from datetime import datetime

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://postgres:Mahlatsi%230310@postgres:5432/campus_safety")
TOPICS = ['safety-reports-topic', 'routes-topic', 'loadshedding-topic']

def connect_db():
    # psycopg2 will parse postgres:// URL
    return psycopg2.connect(DATABASE_URL)

def create_consumer():
    return KafkaConsumer(
        *TOPICS,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

def safe_parse_iso(ts):
    if ts is None:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        try:
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        except Exception:
            return None

def main():
    # retry loop for both DB and Kafka
    while True:
        try:
            consumer = create_consumer()
            print("Connected to Kafka:", KAFKA_BROKER)
            break
        except errors.NoBrokersAvailable:
            print("Kafka not available, retrying in 5s...")
            time.sleep(5)

    db_conn = None
    while True:
        try:
            db_conn = connect_db()
            db_conn.autocommit = False
            cursor = db_conn.cursor()
            print("Connected to Postgres")
            break
        except Exception as e:
            print("Postgres not ready:", e)
            time.sleep(3)

    try:
        for message in consumer:
            topic = message.topic
            data = message.value
            try:
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
                            float(data.get('lat')) if data.get('lat') is not None else None,
                            float(data.get('lon')) if data.get('lon') is not None else None,
                            safe_parse_iso(data.get('timestamp'))
                        )
                    )
                elif topic == 'routes-topic':
                    cursor.execute(
                        """
                        INSERT INTO safe_routes (origin, destination, origin_coords, destination_coords, risk_score, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            data.get('origin'),
                            data.get('destination'),
                            data.get('origin_coords'),
                            data.get('destination_coords'),
                            float(data.get('risk_score')) if data.get('risk_score') is not None else None,
                            safe_parse_iso(data.get('timestamp'))
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
                            int(data.get('stage')) if data.get('stage') is not None else None,
                            safe_parse_iso(data.get('start_time')),
                            safe_parse_iso(data.get('end_time'))
                        )
                    )
                else:
                    print("Unknown topic:", topic)

                db_conn.commit()
                print(f"Inserted data from topic {topic}: {data}")
            except Exception as e:
                db_conn.rollback()
                print("Failed to insert record:", e, "data:", data)
    except KeyboardInterrupt:
        print("Consumer interrupted, exiting.")
    finally:
        if db_conn:
            db_conn.close()
        try:
            consumer.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()