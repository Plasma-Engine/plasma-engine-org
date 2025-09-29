-- Initialize PostgreSQL for Plasma Engine
-- This script runs automatically when PostgreSQL container starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas for each service
CREATE SCHEMA IF NOT EXISTS gateway;
CREATE SCHEMA IF NOT EXISTS research;
CREATE SCHEMA IF NOT EXISTS brand;
CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS agent;
CREATE SCHEMA IF NOT EXISTS shared;

-- Create a shared users table (used by gateway)
CREATE TABLE IF NOT EXISTS shared.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create documents table for research service
CREATE TABLE IF NOT EXISTS research.documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    content_type VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create embeddings table for vector search
CREATE TABLE IF NOT EXISTS research.embeddings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID REFERENCES research.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    chunk_text TEXT,
    embedding vector(3072),  -- For text-embedding-3-large
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx
ON research.embeddings
USING hnsw (embedding vector_cosine_ops);

-- Create social_mentions table for brand service
CREATE TABLE IF NOT EXISTS brand.social_mentions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    external_id VARCHAR(255),
    author VARCHAR(255),
    content TEXT,
    url TEXT,
    sentiment_score FLOAT,
    engagement_metrics JSONB,
    collected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create content_items table for content service
CREATE TABLE IF NOT EXISTS content.content_items (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content TEXT,
    metadata JSONB,
    status VARCHAR(50) DEFAULT 'draft',
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create workflows table for agent service
CREATE TABLE IF NOT EXISTS agent.workflows (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create workflow_executions table
CREATE TABLE IF NOT EXISTS agent.workflow_executions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    workflow_id UUID REFERENCES agent.workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_social_mentions_platform ON brand.social_mentions(platform);
CREATE INDEX IF NOT EXISTS idx_social_mentions_collected_at ON brand.social_mentions(collected_at);
CREATE INDEX IF NOT EXISTS idx_content_items_status ON content.content_items(status);
CREATE INDEX IF NOT EXISTS idx_content_items_type ON content.content_items(type);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON agent.workflow_executions(status);

-- Grant permissions (adjust as needed)
GRANT USAGE ON SCHEMA gateway TO plasma;
GRANT USAGE ON SCHEMA research TO plasma;
GRANT USAGE ON SCHEMA brand TO plasma;
GRANT USAGE ON SCHEMA content TO plasma;
GRANT USAGE ON SCHEMA agent TO plasma;
GRANT USAGE ON SCHEMA shared TO plasma;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gateway TO plasma;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA research TO plasma;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA brand TO plasma;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA content TO plasma;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA agent TO plasma;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA shared TO plasma;

-- Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON shared.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON research.documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_items_updated_at BEFORE UPDATE ON content.content_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON agent.workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO shared.users (email, password_hash, full_name, is_admin)
VALUES ('admin@plasma-engine.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.C0', 'Admin User', true)
ON CONFLICT (email) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Plasma Engine database initialization complete!';
END $$;