# Risks & Assumptions

## 1. Contradictions Identified & Resolved
*   **Contradiction:** User requirements stated "Do not build this as a generic chatbot," but often LLM apps default to a chat UI.
*   **Resolution:** The UI Architecture explicitly defines a dashboard/workspace model. Chat is heavily restricted to a "Clarification" sidebar solely for gathering missing facts.

## 2. Missing Components Identified & Added
*   **Citation Verification:** Initially under-specified. A dedicated post-generation verification step has been added to the RAG design to prevent hallucinated citations.
*   **Evaluation Framework:** Need a mechanism to measure RAG accuracy.

## 3. Unnecessary Complexity Avoided
*   **Avoided:** Cross-encoder reranking models. For the MVP, `pgvector` semantic search combined with strict SQL metadata filtering (jurisdiction/domain) is sufficient and much faster.
*   **Avoided:** Live web scraping. The MVP will use a static, pre-ingested corpus to ensure reliability and traceability.

## 4. Security Risks
*   **Risk:** PII or proprietary innovation formulations leaking into model training data.
*   **Mitigation:** Use enterprise API endpoints (e.g., OpenAI API with zero-data-retention policies) or local models if hardware permits. Do not use consumer web interfaces.

## 5. RAG-Specific Risks
*   **Risk:** Naive chunking destroys legal context (e.g., splitting "provided that..." from its parent section).
*   **Mitigation:** Structure-aware parsing. The ingestion pipeline must tag chunks with their explicit legal hierarchy (`hierarchy_level_1`, etc.).

## 6. Citation-Grounding Weaknesses
*   **Risk:** LLMs generating plausible but fake section numbers.
*   **Mitigation:** The prompt forces the LLM to output specific `[chunk_id]` references. The backend physically verifies these IDs exist in the retrieved context payload before rendering the response.

## 7. Jurisdiction Leakage Risks
*   **Risk:** Semantic search pulling an international treaty when assessing an Indian query.
*   **Mitigation:** Vector searches are *always* prefaced by a hard SQL `WHERE jurisdiction = 'india'` clause.

## 8. Classification Reliability Risks
*   **Risk:** LLM arbitrarily classifying products incorrectly.
*   **Mitigation:** Use structured outputs (JSON schema) and combine with deterministic pre-filters. Emphasize that classification is "preliminary" and for decision-support only.

## 9. Knowledge-Base Maintenance Risks
*   **Risk:** Outdated laws.
*   **Mitigation:** Database schema includes `status` (active/superseded) and `version` columns.

## 10. Too Ambitious for SIH MVP
*   **Scope Cut:** Fully autonomous agent swarms, automated legal filing, and exhaustive global coverage are deferred. The focus is strictly on a reliable, traceable assessment workflow for India + core International frameworks.
