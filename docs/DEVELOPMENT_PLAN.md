# Development Plan

## PHASE 0: Architecture and Planning (Completed)
*   Initial project inspection.
*   Generation of architecture docs, schemas, and API contracts.
*   Identification of risks and required mitigations.

## PHASE 1: Project Scaffolding + Database + Configuration
*   Initialize Git repository.
*   Setup `docker-compose.yml` with PostgreSQL + `pgvector`.
*   Create backend FastAPI boilerplate and Alembic migrations for the schema.
*   Create frontend Next.js boilerplate with Tailwind.

## PHASE 2: Knowledge Ingestion + Corpus + Vector Search
*   Create a local folder structure for the corpus (`knowledge_base/india`, `knowledge_base/international`).
*   Develop Python scripts to parse PDF/HTML.
*   Implement structure-aware chunking.
*   Generate embeddings and load them into `pgvector` via SQLAlchemy.

## PHASE 3: RAG + Citation Architecture
*   Implement the core retrieval pipeline (Hybrid Search).
*   Implement prompt templates for grounded generation.
*   Build the post-generation citation verification module.

## PHASE 4: Classification + IP/TK/ABS Assessment
*   Develop the specific assessment modules.
*   Implement the intent detection and missing-information identification logic (Clarification loop).
*   Structure the LLM outputs using Pydantic.

## PHASE 5: Assessment Orchestration + Action Plan
*   Tie the modules together into the main `/analyze` API endpoint.
*   Implement the Action Plan generator.
*   Implement the Human Escalation brief generator.

## PHASE 6: Frontend UX
*   Build the Next.js UI components (Assessment Cards, Evidence Drawer).
*   Integrate frontend with backend APIs.
*   Implement the strict India/International jurisdiction visual separation.

## PHASE 7: Multilingual Support
*   Integrate translation layers (or multilingual prompts) to support Hindi input and output while preserving English citations/sources.

## PHASE 8: Evaluation + Security + Hardening
*   Run the evaluation dataset against the RAG pipeline.
*   Review input validation and prompt injection defenses.
*   Finalize error handling and logging.

## PHASE 9: Browser-Based End-to-End Verification
*   Use browser automation to run through the exact SIH demo script.
*   Verify UI behavior, citation linking, and state management.
