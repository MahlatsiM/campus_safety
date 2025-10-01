import json
import random
import time
import uuid
from kafka import KafkaProducer
from datetime import datetime

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Bounding square for reports
LAT_MIN, LAT_MAX = -28.764947, -28.724177
LON_MIN, LON_MAX = 24.722326, 24.794486

REPORT_TYPES = ["Harrasment", "Sexual Assault", "Assault", "Hazard", "Theft", "Suspicious Activity", "Other"]
USER_IDS = [f"user{i}" for i in range(1, 31)]  # user1 - user30

def generate_user(user_id):
    return {
        "user_id": user_id,
        "session_cookie": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat()
    }

def generate_random_report():
    return {
        "user_id": random.choice(USER_IDS),
        "report_type": random.choice(REPORT_TYPES),
        "description": "Auto-generated report",
        "latitude": round(random.uniform(LAT_MIN, LAT_MAX), 6),
        "longitude": round(random.uniform(LON_MIN, LON_MAX), 6),
        "created_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Send users once at startup
    for user_id in USER_IDS:
        user = generate_user(user_id)
        producer.send("users-topic", user)
        print(f"Produced user: {user}")
    producer.flush()
    print("All users produced. Starting report generation...")

    # Then continuously send reports
    while True:
        report = generate_random_report()
        producer.send("safety-reports-topic", report)
        producer.flush()
        print(f"Produced report: {report}")
        time.sleep(1)