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

CREATE TABLE safe_routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(255),
    destination VARCHAR(255),
    origin_coords TEXT,       -- store as tuple "(lat, lon)"
    destination_coords TEXT,
    risk_score FLOAT,
    timestamp TIMESTAMP
);

CREATE TABLE green_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    lat FLOAT,
    lon FLOAT,
    radius_m FLOAT,          -- radius to define “safe zone” around the point
    type VARCHAR(50)         -- campus, police station, hospital
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