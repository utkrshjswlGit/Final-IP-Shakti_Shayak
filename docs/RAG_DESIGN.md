# RAG Design Pipeline

The RAG pipeline prioritizes evidence, jurisdiction boundaries, and safe abstention.

## 1. Document Ingestion (Offline)
*   **Parsing:** Legal PDFs and HTML are parsed using structure-aware libraries (e.g., `unstructured`).
*   **Chunking:** Instead of naive token-based chunking (which breaks legal clauses in half), chunking is hierarchical. A chunk represents a specific Article, Section, or Rule.
*   **Metadata Extraction:** Every chunk is tagged with its parent document's jurisdiction, authority, domain, and specific section number.
*   **Embedding:** Indexed into `pgvector`.

## 2. Query Analysis & Routing (Online)
*   **Input:** User innovation + assessment domain (e.g., "Assess IP opportunity for Ashwagandha formulation").
*   **Intent Detection:** Determine if the query is relevant to IP/TK/ABS.
*   **Query Expansion:** Expand Ayurvedic terms (e.g., Ashwagandha -> Withania somnifera) using a predefined synonym dictionary to improve semantic matching.

## 3. Retrieval
*   **Pre-filtering:** Strict SQL `WHERE jurisdiction = 'target_jurisdiction' AND status = 'active'`. This is a non-negotiable step to prevent jurisdiction leakage.
*   **Hybrid Search:**
    *   *Semantic Search:* `pgvector` cosine similarity.
    *   *Lexical Search:* BM25 (or Postgres Full Text Search) to ensure exact matches on section numbers or specific chemical/botanical names are not missed.
*   **Context Windowing:** Retrieve the top N chunks. If chunks are too small, retrieve surrounding sibling chunks to provide the LLM with legal context.

## 4. Grounded Generation
*   The LLM prompt is heavily constrained.
*   **Instruction:** "You must base your answer strictly on the provided context. If the context does not contain the answer, output 'Insufficient evidence'. For every claim, you MUST append a citation ID like `[chunk_uuid]`."
*   **Format:** Forced JSON output for structured assessment rendering.

## 5. Post-Generation Citation Verification
*   This is the critical differentiator from generic chatbots.
*   The system parses the generated JSON. For every `[chunk_uuid]` cited:
    1. It verifies the chunk was actually in the retrieved context.
    2. (Optional MVP enhancement): A small, fast LLM pass checks if the cited chunk actually entails the claim made.
*   If verification fails, the claim is redacted or the confidence score is dropped to `INSUFFICIENT`.

## 6. Confidence Scoring & Abstention
*   Confidence is calculated deterministically based on:
    *   Presence of Tier 1 sources in the retrieved context.
    *   Citation density (how many claims have verified citations).
    *   If no relevant chunks are found above a similarity threshold, the system immediately short-circuits to Abstention ("Insufficient evidence").
