from kafka import KafkaProducer
import json, time, random
from datetime import datetime, timedelta

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',  # use container service name
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

locations = [
    {"name": "North Campus", "lat": -28.7383, "lon": 24.7635},
    {"name": "South Campus", "lat": -28.7414, "lon": 24.7702},
    {"name": "City Residence", "lat": -28.7402, "lon": 24.7715},
    {"name": "Student Village", "lat": -28.7431, "lon": 24.7668}
]

incident_types = ["theft", "harassment", "suspicious_activity", "accident"]

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
    print("Streaming synthetic campus safety data...")
    try:
        while True:
            producer.send("safety-reports-topic", value=generate_safety_report())
            producer.send("routes-topic", value=generate_route())
            producer.send("loadshedding-topic", value=generate_loadshedding())
            time.sleep(random.uniform(1,5))  # random intervals
    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        producer.close()