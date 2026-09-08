# Database Schema

The system uses PostgreSQL with the `pgvector` extension.

## Core Tables

### 1. `users`
*   `id` (UUID, PK)
*   `email` (VARCHAR, Unique)
*   `hashed_password` (VARCHAR)
*   `role` (VARCHAR) - e.g., 'user', 'admin'
*   `created_at` (TIMESTAMP)

### 2. `sessions`
*   `id` (UUID, PK)
*   `user_id` (UUID, FK -> users.id)
*   `title` (VARCHAR)
*   `current_jurisdiction` (VARCHAR) - ENUM: 'india', 'international'
*   `created_at` (TIMESTAMP)

### 3. `assessments`
Stores the structured output of the evaluation pipeline.
*   `id` (UUID, PK)
*   `session_id` (UUID, FK -> sessions.id)
*   `innovation_description` (TEXT) - Encrypted at rest.
*   `status` (VARCHAR) - ENUM: 'intake', 'clarifying', 'analyzing', 'complete', 'escalated'
*   `classification_data` (JSONB)
*   `ip_assessment` (JSONB)
*   `tk_assessment` (JSONB)
*   `abs_assessment` (JSONB)
*   `action_plan` (JSONB)
*   `created_at` (TIMESTAMP)

### 4. `documents` (Knowledge Base Metadata)
*   `id` (UUID, PK)
*   `title` (VARCHAR)
*   `authority` (VARCHAR) - e.g., 'Ministry of Ayush', 'WIPO'
*   `jurisdiction` (VARCHAR) - ENUM: 'india', 'international'
*   `domain` (VARCHAR) - e.g., 'Patent', 'Biodiversity'
*   `document_type` (VARCHAR) - e.g., 'Act', 'Rule', 'Guideline'
*   `version` (VARCHAR)
*   `status` (VARCHAR) - ENUM: 'active', 'superseded'
*   `source_url` (VARCHAR)
*   `trust_tier` (INTEGER) - 1 (Primary), 2 (Explanatory), 3 (Secondary)
*   `content_hash` (VARCHAR) - For deduplication.

### 5. `document_chunks` (Vector Store)
*   `id` (UUID, PK)
*   `document_id` (UUID, FK -> documents.id)
*   `content` (TEXT) - The actual text chunk.
*   `embedding` (VECTOR) - `pgvector` column (e.g., 1536 dimensions for OpenAI).
*   `hierarchy_level_1` (VARCHAR) - e.g., 'Chapter II'
*   `hierarchy_level_2` (VARCHAR) - e.g., 'Section 3'
*   `hierarchy_level_3` (VARCHAR) - e.g., 'Subsection (p)'
*   `page_num` (INTEGER)

### 6. `audit_logs`
*   `id` (UUID, PK)
*   `user_id` (UUID, FK)
*   `action` (VARCHAR)
*   `target_resource` (VARCHAR)
*   `timestamp` (TIMESTAMP)

## Design Notes
*   **Jurisdiction Filtering:** The `jurisdiction` column in `documents` allows strict filtering during RAG.
*   **JSONB Storage:** `JSONB` is used for assessment outputs because the internal schema of the AI analysis might evolve, but it remains queryable.
*   **Structure Preservation:** The `hierarchy_level_*` columns in `document_chunks` ensure that when a chunk is retrieved, the LLM and the user know exactly where it came from (e.g., Section 3(p) of the Patents Act), not just an arbitrary text blob.
