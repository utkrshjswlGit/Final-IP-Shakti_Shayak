# System Architecture

## Overview
IP-SAKTI Sahayak is a decision-support platform, not a generic chatbot. The architecture is designed to support a rigorous, evidence-first workflow: **Intake -> Clarification -> Classification -> Assessment -> Action Plan**.

## Core Components

### 1. Frontend (Presentation Layer)
*   **Framework:** Next.js (React, TypeScript)
*   **Styling:** Tailwind CSS
*   **Responsibility:** Providing a professional assessment workspace. Managing the state of the user's workflow. Rendering structured data (assessments, citations) cleanly.

### 2. Backend (Application & API Layer)
*   **Framework:** FastAPI (Python)
*   **Responsibility:** Exposing RESTful endpoints, orchestrating the assessment workflow, managing state, and enforcing business logic.
*   **Modules:**
    *   `auth`: User authentication and session management.
    *   `workflow`: Orchestrates the step-by-step assessment process.
    *   `classification`: Hybrid rule-based and LLM-assisted product categorization.
    *   `assessment`: Domain-specific evaluators (IP, TK, ABS).

### 3. AI & Retrieval Layer (RAG Service)
*   **Framework:** Custom LangChain/LlamaIndex abstractions to ensure absolute control over the prompt and context.
*   **Responsibility:** Query intent detection, jurisdiction-filtered hybrid retrieval, grounded generation, and citation verification.
*   **LLM Provider:** Configurable (e.g., OpenAI API or Azure OpenAI) utilizing strictly structured outputs (JSON).

### 4. Data Layer
*   **Relational Database:** PostgreSQL.
*   **Vector Database:** `pgvector` extension within PostgreSQL.
*   **Responsibility:** Storing user data, assessment history, audit logs, and the vectorized knowledge base. Using a unified database reduces infrastructure complexity while maintaining transactional guarantees.

## Critical Architectural Decisions
1.  **Single-Tenant Database per Session:** To prevent jurisdiction leakage, the API enforces strict jurisdiction context at the database query level. `WHERE jurisdiction = '...'` is applied *before* vector similarity search.
2.  **Structured LLM Outputs:** The LLM is forced to output JSON matching Pydantic schemas. It is never allowed to return unstructured Markdown directly to the UI for substantive assessments.
3.  **Stateless RAG:** The RAG pipeline itself is stateless. Conversation history is explicitly managed and injected by the backend workflow service only when clarifying missing facts.
4.  **No Automated Scrapers:** For the MVP, the knowledge base is a curated, static set of highly authoritative documents ingested via a dedicated pipeline, rather than an error-prone live web scraper.
