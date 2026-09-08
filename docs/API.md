# API Map

The backend exposes a RESTful JSON API using FastAPI.

## Authentication
*   `POST /api/v1/auth/login` -> Returns JWT
*   `POST /api/v1/auth/logout`

## Sessions & Assessments
The core workflow is managed through assessment endpoints.

*   `POST /api/v1/sessions`
    *   Creates a new workspace session.
*   `GET /api/v1/sessions`
    *   Lists historical sessions.
*   `GET /api/v1/sessions/{session_id}`

*   `POST /api/v1/sessions/{session_id}/assessments/init`
    *   **Payload:** `{ "innovation_description": "...", "jurisdiction": "india" }`
    *   **Action:** Starts the intake process. Detects intent and missing information.
    *   **Returns:** Clarification questions or proceeds to classification.

*   `POST /api/v1/sessions/{session_id}/assessments/clarify`
    *   **Payload:** `{ "answers": [...] }`
    *   **Action:** Submits answers to clarification questions.

*   `POST /api/v1/sessions/{session_id}/assessments/analyze`
    *   **Action:** Triggers the heavy RAG pipelines (Classification, IP, TK, ABS). This may be a long-polling or async job endpoint returning a task ID in a production scenario, but for MVP it can be a synchronous endpoint with a larger timeout or server-sent events (SSE) for progress updates.

*   `GET /api/v1/sessions/{session_id}/assessments/result`
    *   **Returns:** The structured assessment JSON (Classification, IP Map, Confidence, Action Plan).

## Evidence & Citations
*   `GET /api/v1/evidence/{chunk_id}`
    *   Retrieves the exact document chunk and metadata for a specific citation ID returned in the assessment.

## Human Escalation
*   `POST /api/v1/sessions/{session_id}/escalate`
    *   Generates the structured human-expert brief based on the current assessment state.

## System / Admin
*   `GET /api/v1/health`
*   `POST /api/v1/admin/documents/ingest` (Protected)
