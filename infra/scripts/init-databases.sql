-- PostgreSQL Initialization Script for Plasma Engine
-- Creates all required databases and extensions

-- Create plasma_research database
CREATE DATABASE plasma_research;
GRANT ALL PRIVILEGES ON DATABASE plasma_research TO plasma;

-- Create plasma_content database
CREATE DATABASE plasma_content;
GRANT ALL PRIVILEGES ON DATABASE plasma_content TO plasma;

-- Create plasma_brand database
CREATE DATABASE plasma_brand;
GRANT ALL PRIVILEGES ON DATABASE plasma_brand TO plasma;

-- Create plasma_agent database
CREATE DATABASE plasma_agent;
GRANT ALL PRIVILEGES ON DATABASE plasma_agent TO plasma;

-- Create plasma_gateway database
CREATE DATABASE plasma_gateway;
GRANT ALL PRIVILEGES ON DATABASE plasma_gateway TO plasma;

-- Create plasma_core database
CREATE DATABASE plasma_core;
GRANT ALL PRIVILEGES ON DATABASE plasma_core TO plasma;

-- Connect to each database and create necessary extensions
\c plasma_research;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c plasma_content;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c plasma_brand;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c plasma_agent;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c plasma_gateway;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c plasma_core;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";