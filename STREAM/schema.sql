-- Users table (updated for auth)
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    hashed_password TEXT NOT NULL,
    roles TEXT[],  -- optional, e.g., admin, viewer
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP,
    session_cookie TEXT
);

-- Optional: Blocked users
CREATE TABLE IF NOT EXISTS blocked_users (
    user_id INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    blocked_until TIMESTAMP,
    reason TEXT
);

-- Routes table
CREATE TABLE IF NOT EXISTS routes (
    route_id SERIAL PRIMARY KEY,
    start_lat DOUBLE PRECISION,
    start_lon DOUBLE PRECISION,
    end_lat DOUBLE PRECISION,
    end_lon DOUBLE PRECISION
);

-- Safety reports
CREATE TABLE IF NOT EXISTS safety_reports (
    report_id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) REFERENCES users(user_id) ON DELETE SET NULL,
    report_type TEXT, -- hazard, theft, suspicious activity, etc.
    description TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Green areas
CREATE TABLE IF NOT EXISTS green_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    radius_meters DOUBLE PRECISION,
    type VARCHAR(50) -- campus, security outpost, etc.
);