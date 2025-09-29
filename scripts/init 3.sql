-- Plasma Engine PostgreSQL Initialization Script
-- Creates all necessary databases and extensions for development

-- Create databases for each service
CREATE DATABASE plasma_gateway;
CREATE DATABASE plasma_research;
CREATE DATABASE plasma_brand;
CREATE DATABASE plasma_content;
CREATE DATABASE plasma_agent;

-- Connect to plasma_gateway database
\c plasma_gateway;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Connect to plasma_research database
\c plasma_research;

-- Create extensions including pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Connect to plasma_brand database
\c plasma_brand;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Connect to plasma_content database
\c plasma_content;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Connect to plasma_agent database
\c plasma_agent;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create a read-only user for monitoring
CREATE USER monitoring WITH PASSWORD 'monitoring_password';
GRANT CONNECT ON DATABASE plasma_gateway TO monitoring;
GRANT CONNECT ON DATABASE plasma_research TO monitoring;
GRANT CONNECT ON DATABASE plasma_brand TO monitoring;
GRANT CONNECT ON DATABASE plasma_content TO monitoring;
GRANT CONNECT ON DATABASE plasma_agent TO monitoring;

-- Grant read permissions on all tables (will apply to future tables)
\c plasma_gateway;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitoring;

\c plasma_research;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitoring;

\c plasma_brand;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitoring;

\c plasma_content;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitoring;

\c plasma_agent;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO monitoring;