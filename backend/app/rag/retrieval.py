"""Hybrid retrieval engine for evidence extraction."""

import json
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.document import Document, DocumentChunk
from app.core.llm import get_embeddings
from app.core.logging import get_logger

logger = get_logger(__name__)

class RetrievedEvidence:
    def __init__(self, chunk: DocumentChunk, document: Document, score: float):
        self.chunk = chunk
        self.document = document
        self.score = score

def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a * a for a in vec1) ** 0.5
    norm_b = sum(b * b for b in vec2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

async def retrieve_evidence(
    query: str, 
    jurisdiction: str, 
    db: AsyncSession, 
    top_k: int = 5
) -> List[RetrievedEvidence]:
    """Retrieve top chunks for a query using hybrid search + jurisdiction filtering."""
    
    # 1. Embed query
    query_vector = get_embeddings([query])[0]
    
    # 2. Strict Pre-filtering by Jurisdiction
    # In production with pgvector, we would do this in the SQL query:
    # select(DocumentChunk).join(Document)...order_by(DocumentChunk.embedding.cosine_distance(query_vector))
    # For SQLite cross-compatibility and testing, we fetch filtered chunks and compute locally.
    
    stmt = (
        select(DocumentChunk)
        .join(Document)
        .where(Document.jurisdiction == jurisdiction)
        .where(Document.status == "active")
        .options(selectinload(DocumentChunk.document))
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()
    
    if not chunks:
        logger.info("retrieval_no_chunks_for_jurisdiction", jurisdiction=jurisdiction)
        return []
        
    # 3. Compute Semantic Scores
    semantic_scores = []
    for c in chunks:
        # If DB is SQLite, embedding is stored as JSON string of floats
        # If pgvector is used, it might be a list or ndarray
        if isinstance(c.embedding, str):
            try:
                vec = json.loads(c.embedding)
            except Exception:
                vec = [0.0] * len(query_vector)
        elif hasattr(c.embedding, "__iter__"):
            vec = list(c.embedding)
        else:
            vec = [0.0] * len(query_vector)
            
        score = _cosine_similarity(query_vector, vec)
        semantic_scores.append((c, score))
        
    # Sort by semantic score descending
    semantic_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 4. Lexical Search using BM25
    try:
        from rank_bm25 import BM25Okapi
        tokenized_corpus = [c.content.lower().split() for c in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.lower().split()
        lexical_scores_raw = bm25.get_scores(tokenized_query)
        
        lexical_scores = [(chunks[i], score) for i, score in enumerate(lexical_scores_raw)]
        lexical_scores.sort(key=lambda x: x[1], reverse=True)
    except ImportError:
        logger.warning("rank_bm25_not_installed_skipping_lexical")
        lexical_scores = [(c, 0.0) for c in chunks]

    # 5. Reciprocal Rank Fusion (RRF)
    # RRF Score = 1 / (k + rank)
    k_rrf = 60
    rrf_scores: Dict[str, float] = {}
    
    def apply_rrf(scored_list):
        current_rank = 0
        last_score = None
        for i, (chunk, score) in enumerate(scored_list):
            if score != last_score:
                current_rank = i
                last_score = score
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + (1.0 / (k_rrf + current_rank + 1))
            
    apply_rrf(semantic_scores)
    apply_rrf(lexical_scores)
        
    # Combine back to list and sort
    final_results = []
    for chunk in chunks:
        final_results.append(RetrievedEvidence(chunk=chunk, document=chunk.document, score=rrf_scores.get(chunk.id, 0.0)))
        
    final_results.sort(key=lambda x: x.score, reverse=True)
    
    logger.info("retrieval_complete", query=query, results=min(top_k, len(final_results)))
    return final_results[:top_k]
