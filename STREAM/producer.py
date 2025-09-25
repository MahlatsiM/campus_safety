from kafka import KafkaProducer, errors
import json, time, random
from datetime import datetime, timedelta

# ---------------------------
# Kafka connection
# ---------------------------
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:29092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Connected to Kafka broker")
        break
    except errors.NoBrokersAvailable:
        print("Kafka broker not ready, retrying in 5 sec...")
        time.sleep(5)
else:
    raise Exception("Kafka broker not available after 50 seconds")

# ---------------------------
# Bounding box for Kimberley Square (for yellow/red routes)
# ---------------------------
LAT_MIN, LAT_MAX = -28.764947, -28.723893
LON_MIN, LON_MAX = 24.722326, 24.794456

def random_location():
    return {
        "lat": round(random.uniform(LAT_MIN, LAT_MAX), 6),
        "lon": round(random.uniform(LON_MIN, LON_MAX), 6)
    }

# ---------------------------
# Safety reports
# ---------------------------
incident_types = ["theft", "harassment", "suspicious_activity", "accident"]

def generate_safety_report():
    loc = random_location()
    # Randomize timestamp within past 24 hours
    timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 59))
    return {
        "reporter": f"user{random.randint(1,100)}",
        "category": random.choice(incident_types),
        "description": "Synthetic safety event",
        "lat": loc["lat"] + random.uniform(-0.001, 0.001),
        "lon": loc["lon"] + random.uniform(-0.001, 0.001),
        "timestamp": timestamp.isoformat()
    }

# ---------------------------
# Predefined green routes
# ---------------------------
green_routes = [
    ((-28.747768, 24.765804), (-28.743639, 24.762616)),
    ((-28.748184, 24.765766), (-28.748115, 24.758987)),
    ((-28.752487, 24.763112), (-28.746789, 24.762963)),
    ((-28.747846, 24.766240), (-28.744543, 24.771700)),
    ((-28.747020, 24.766517), (-28.742686, 24.768342)),
    ((-28.751240, 24.763011), (-28.752531, 24.755070))
]

def generate_route():
    # Decide risk type
    risk_type = random.choices(["green", "yellow", "red"], weights=[0.6, 0.25, 0.15])[0]

    if risk_type == "green":
        start, end = random.choice(green_routes)
        risk_score = round(random.uniform(0, 0.39), 2)
    else:
        # Random yellow/red routes around Kimberley Square
        start_loc = random_location()
        end_loc = random_location()
        start = (start_loc["lat"], start_loc["lon"])
        end = (end_loc["lat"], end_loc["lon"])
        if risk_type == "yellow":
            risk_score = round(random.uniform(0.4, 0.74), 2)
        else:
            risk_score = round(random.uniform(0.75, 1.0), 2)

    # Random timestamp within past 24 hours
    timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 59))

    return {
        "origin": f"({start[0]}, {start[1]})",
        "destination": f"({end[0]}, {end[1]})",
        "risk_score": risk_score,
        "timestamp": timestamp.isoformat()
    }

# ---------------------------
# Loadshedding generator
# ---------------------------
def generate_loadshedding():
    area = f"Zone-{random.randint(1,5)}"
    stage = random.randint(1, 6)
    start = datetime.utcnow() - timedelta(hours=random.randint(0, 24))
    end = start + timedelta(hours=2)
    return {
        "area": area,
        "stage": stage,
        "start_time": start.isoformat(),
        "end_time": end.isoformat()
    }

# ---------------------------
# Main loop
# ---------------------------
if __name__ == "__main__":
    print("Streaming synthetic campus safety data...")
    try:
        while True:
            report = generate_safety_report()
            producer.send("safety-reports-topic", value=report)
            print("Sent safety report:", report)

            route = generate_route()
            producer.send("routes-topic", value=route)
            print("Sent route:", route)

            loadshedding = generate_loadshedding()
            producer.send("loadshedding-topic", value=loadshedding)
            print("Sent loadshedding:", loadshedding)

            time.sleep(2)
    except KeyboardInterrupt:
        print("Producer stopped.")
    finally:
        producer.close()
