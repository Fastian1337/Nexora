-- ============================================
-- Nexora Platform — PostgreSQL Initialization
-- ============================================
-- This script runs when the PostgreSQL container
-- is first created. It sets up required extensions.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for AI embeddings
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Nexora database initialized with extensions: uuid-ossp, vector, pg_trgm';
END
$$;
