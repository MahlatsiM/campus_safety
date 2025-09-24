-- Safety reports
CREATE TABLE IF NOT EXISTS safety_reports (
    report_id SERIAL PRIMARY KEY,
    reporter TEXT,
    category TEXT,
    description TEXT,
    lat FLOAT,
    lon FLOAT,
    timestamp TIMESTAMP
);

-- Routes safety score
CREATE TABLE IF NOT EXISTS safe_routes (
    route_id SERIAL PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    risk_score FLOAT,
    timestamp TIMESTAMP
);

-- Load-shedding
CREATE TABLE IF NOT EXISTS loadshedding (
    id SERIAL PRIMARY KEY,
    area TEXT,
    stage INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);