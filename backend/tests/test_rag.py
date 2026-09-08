"""Tests for RAG ingestion and hybrid retrieval."""

import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.ingestion import ingest_markdown_document
from app.rag.retrieval import retrieve_evidence
from app.models.document import Document, DocumentChunk
from sqlalchemy import select

@pytest.fixture
def corpus_dir():
    # Construct path to the corpus directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(current_dir), "corpus")

@pytest.mark.asyncio
async def test_ingest_documents(db_session: AsyncSession, corpus_dir: str):
    """Test that markdown files are successfully parsed, chunked, and stored."""
    bd_act_path = os.path.join(corpus_dir, "bd_act_2002.md")
    patents_act_path = os.path.join(corpus_dir, "patents_act_1970.md")
    
    # Ingest BD Act
    doc1 = await ingest_markdown_document(bd_act_path, db_session)
    assert doc1 is not None
    assert doc1.title == "The Biological Diversity Act, 2002"
    assert doc1.jurisdiction == "india"
    
    # Ingest Patents Act
    doc2 = await ingest_markdown_document(patents_act_path, db_session)
    assert doc2 is not None
    assert doc2.title == "The Patents Act, 1970"
    
    # Verify chunks are created
    chunks_result = await db_session.execute(select(DocumentChunk).where(DocumentChunk.document_id == doc1.id))
    chunks = chunks_result.scalars().all()
    assert len(chunks) > 0
    
    # Ensure they have embeddings and metadata
    for chunk in chunks:
        assert chunk.embedding is not None
        assert chunk.hierarchy_level_1 is not None
        assert chunk.content is not None

@pytest.mark.asyncio
async def test_retrieve_evidence_jurisdiction_filter(db_session: AsyncSession, corpus_dir: str):
    """Test that retrieval strictly filters by jurisdiction."""
    # Ensure docs are ingested
    await ingest_markdown_document(os.path.join(corpus_dir, "bd_act_2002.md"), db_session)
    
    # We query for BD Act related terms but ask for 'international' jurisdiction
    results = await retrieve_evidence(
        query="National Biodiversity Authority approval",
        jurisdiction="international",  # None of our mock docs are international
        db=db_session,
        top_k=5
    )
    assert len(results) == 0

@pytest.mark.asyncio
async def test_retrieve_evidence_semantic_lexical(db_session: AsyncSession, corpus_dir: str):
    """Test hybrid retrieval returns relevant results."""
    # Ensure docs are ingested
    await ingest_markdown_document(os.path.join(corpus_dir, "bd_act_2002.md"), db_session)
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    
    # Query 1: Patents Act
    results = await retrieve_evidence(
        query="mathematical business method computer programme",
        jurisdiction="india",
        db=db_session,
        top_k=3
    )
    assert len(results) > 0
    # The top result should be from the Patents Act
    assert "Patents Act" in results[0].document.title
    assert "Section 3" in results[0].chunk.hierarchy_level_2
    
    # Query 2: BD Act
    results2 = await retrieve_evidence(
        query="transfer results research biological resources non-citizen",
        jurisdiction="india",
        db=db_session,
        top_k=3
    )
    assert len(results2) > 0
    assert "Biological Diversity Act" in results2[0].document.title
    assert "Section 4" in results2[0].chunk.hierarchy_level_2
