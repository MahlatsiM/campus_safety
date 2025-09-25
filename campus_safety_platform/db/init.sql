-- init.sql: executed once by the Postgres docker entrypoint (first init only)

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254),
    password_hash VARCHAR(255),
    login_count INT DEFAULT 0,
    last_login TIMESTAMP,
    temporal_ban_until TIMESTAMP
);

CREATE TABLE IF NOT EXISTS green_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS green_routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    start_area_id INT REFERENCES green_areas(id) ON DELETE SET NULL,
    end_area_id INT REFERENCES green_areas(id) ON DELETE SET NULL,
    route_coords JSONB, -- store list of [lat, lon] pairs
    patrolled_by VARCHAR(100),
    last_patrolled TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safety_reports (
    id SERIAL PRIMARY KEY,
    reporter VARCHAR(100),
    category VARCHAR(50),
    description TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safe_routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(200),
    destination VARCHAR(200),
    origin_coords TEXT,   -- store tuple string like "(lat, lon)" or JSON
    destination_coords TEXT,
    risk_score DOUBLE PRECISION,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loadshedding (
    id SERIAL PRIMARY KEY,
    area VARCHAR(100),
    stage INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

-- Optional: insert some green_areas (example)
INSERT INTO green_areas (name, type, latitude, longitude) VALUES
('North Campus', 'campus', -28.7383, 24.7635),
('South Campus', 'campus', -28.7414, 24.7702),
('Central Campus', 'campus', -28.7402, 24.7715),
('Student Village', 'campus', -28.7431, 24.7668)
ON CONFLICT DO NOTHING;