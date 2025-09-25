CREATE TABLE IF NOT EXISTS safety_reports (
    id SERIAL PRIMARY KEY,
    reporter VARCHAR(100),
    category VARCHAR(50),
    description TEXT,
    lat FLOAT,
    lon FLOAT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safe_routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100),
    destination VARCHAR(100),
    risk_score FLOAT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loadshedding (
    id SERIAL PRIMARY KEY,
    area VARCHAR(100),
    stage INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);
