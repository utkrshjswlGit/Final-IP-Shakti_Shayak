-- IP-SAKTI Sahayak — PostgreSQL Initialization Script
-- Runs on first container start before Alembic migrations.
-- Only creates the pgvector extension. Schema is managed by Alembic.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
