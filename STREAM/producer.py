from kafka import KafkaProducer, errors
import json, time, random
from datetime import datetime, timedelta

# Wait for Kafka to be ready
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:29092',  # host machine
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Connected to Kafka broker")
        break
    except errors.NoBrokersAvailable:
        print("Kafka broker not ready, retrying in 5 sec...")
        time.sleep(5)
else:
    raise Exception("Kafka broker not available after 50 seconds")

# Bounding box for campus area
LAT_MIN, LAT_MAX = -28.7698, -28.7278
LON_MIN, LON_MAX = 24.7236, 24.7865

def random_location():
    """Generate a random lat/lon within bounding box."""
    return {
        "lat": round(random.uniform(LAT_MIN, LAT_MAX), 6),
        "lon": round(random.uniform(LON_MIN, LON_MAX), 6)
    }

incident_types = ["theft", "harassment", "suspicious_activity", "accident"]

def generate_safety_report():
    loc = random_location()
    return {
        "reporter": f"user{random.randint(1,100)}",
        "category": random.choice(incident_types),
        "description": "Synthetic safety event",
        "lat": loc["lat"] + random.uniform(-0.001, 0.001),
        "lon": loc["lon"] + random.uniform(-0.001, 0.001),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_route():
    start = random_location()
    end = random_location()
    return {
        "origin": f"({start['lat']}, {start['lon']})",
        "destination": f"({end['lat']}, {end['lon']})",
        "risk_score": round(random.uniform(0, 1), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_loadshedding():
    area = f"Zone-{random.randint(1,5)}"
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