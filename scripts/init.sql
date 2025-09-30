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
-- Note: vector extension may need to be installed separately

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