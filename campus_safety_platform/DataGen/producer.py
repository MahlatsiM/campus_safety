from kafka import KafkaProducer
import json, time, random
from datetime import datetime, timedelta

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ---------------------------
# Spatial bounds (Kimberley campus square)
# ---------------------------
LAT_MIN, LAT_MAX = -28.764947, -28.723893
LON_MIN, LON_MAX = 24.722326, 24.794456

incident_types = ["theft", "harassment", "suspicious_activity", "accident"]

# ---------------------------
# Fixed patrol routes
# ---------------------------
routes = [
    {"origin": (-28.747768, 24.765804), "destination": (-28.743639, 24.762616)},
    {"origin": (-28.748184, 24.765766), "destination": (-28.748115, 24.758987)},
    {"origin": (-28.752487, 24.763112), "destination": (-28.746789, 24.762963)},
    {"origin": (-28.747846, 24.766240), "destination": (-28.744543, 24.771700)},
    {"origin": (-28.747020, 24.766517), "destination": (-28.742686, 24.768342)},
    {"origin": (-28.751240, 24.763011), "destination": (-28.752531, 24.755070)},
]

# ---------------------------
# Generators
# ---------------------------
def generate_safety_report():
    return {
        "reporter": f"user{random.randint(1,100)}",
        "category": random.choice(incident_types),
        "description": "Synthetic safety event",
        "lat": random.uniform(LAT_MIN, LAT_MAX),
        "lon": random.uniform(LON_MIN, LON_MAX),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_route():
    r = random.choice(routes)
    return {
        "origin": str(r["origin"]),
        "destination": str(r["destination"]),
        "risk_score": round(random.uniform(0, 1), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_loadshedding():
    area = random.choice([f"Zone-{i}" for i in range(1, 6)])
    stage = random.randint(1, 6)
    start = datetime.utcnow()
    end = start + timedelta(hours=2)
    return {
        "area": area,
        "stage": stage,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    }

# ---------------------------
# Main streaming loop
# ---------------------------
if __name__ == "__main__":
    print("Streaming synthetic campus safety data...")
    try:
        while True:
            producer.send("safety-reports-topic", value=generate_safety_report())
            producer.send("routes-topic", value=generate_route())
            producer.send("loadshedding-topic", value=generate_loadshedding())
            time.sleep(random.uniform(1, 5))
    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        producer.close()
