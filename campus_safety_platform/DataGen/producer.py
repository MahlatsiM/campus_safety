# producer.py
import os
from kafka import KafkaProducer
import json, time, random
from datetime import datetime, timedelta

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

locations = [
    {"name": "North Campus", "lat": -28.7383, "lon": 24.7635},
    {"name": "South Campus", "lat": -28.7414, "lon": 24.7702},
    {"name": "City Residence", "lat": -28.7402, "lon": 24.7715},
    {"name": "Student Village", "lat": -28.7431, "lon": 24.7668}
]

incident_types = ["theft", "harassment", "suspicious_activity", "accident", "other"]

def generate_safety_report():
    loc = random.choice(locations)
    return {
        "reporter": f"user{random.randint(1,100)}",
        "category": random.choice(incident_types),
        "description": "Synthetic safety event",
        "lat": loc["lat"] + random.uniform(-0.001, 0.001),
        "lon": loc["lon"] + random.uniform(-0.001, 0.001),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_route():
    start, end = random.sample(locations, 2)
    return {
        "origin": start["name"],
        "destination": end["name"],
        # store coords as JSON-ish string so consumer can insert safely
        "origin_coords": f"({start['lat']}, {start['lon']})",
        "destination_coords": f"({end['lat']}, {end['lon']})",
        "risk_score": round(random.uniform(0, 1), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_loadshedding():
    area = random.choice([loc["name"] for loc in locations])
    stage = random.randint(1, 6)
    start = datetime.utcnow()
    end = start + timedelta(hours=2)
    return {
        "area": area,
        "stage": stage,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    }

if __name__ == "__main__":
    print("Streaming synthetic campus safety data to Kafka...")
    try:
        while True:
            sr = generate_safety_report()
            producer.send("safety-reports-topic", value=sr)
            print("Sent safety report:", sr)

            route = generate_route()
            producer.send("routes-topic", value=route)
            print("Sent route:", route)

            ls = generate_loadshedding()
            producer.send("loadshedding-topic", value=ls)
            print("Sent loadshedding:", ls)

            # flush occasionally
            producer.flush()
            time.sleep(random.uniform(1, 5))
    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        producer.close()