-- CSRD-Agent Database Initialization
-- Creates the database if not exists (handled by POSTGRES_DB env var)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE csrd_db TO csrd_user;
