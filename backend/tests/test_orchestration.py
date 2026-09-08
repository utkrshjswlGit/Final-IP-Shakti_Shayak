"""Tests for RAG Orchestration edge cases (safe abstention and citation verification)."""

import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.ingestion import ingest_markdown_document
from app.rag.orchestration import assess_query
from app.schemas.rag import AbstentionReason, EvidenceStrength

@pytest.fixture
def corpus_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(current_dir), "corpus")

@pytest.mark.asyncio
async def test_condition_no_relevant_evidence(db_session: AsyncSession, corpus_dir: str):
    # Do NOT ingest any documents
    result = await assess_query("What is the patentability of XYZ?", "india", db_session)
    assert result.abstention_reason == AbstentionReason.NO_EVIDENCE
    assert result.strength == EvidenceStrength.INSUFFICIENT
    assert len(result.claims) == 0

@pytest.mark.asyncio
async def test_condition_wrong_jurisdiction(db_session: AsyncSession, corpus_dir: str):
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    # Query for jurisdiction that doesn't match the ingested doc
    result = await assess_query("Patentability", "international", db_session)
    # Because pre-filtering kicks in, it acts like NO_EVIDENCE in the target jurisdiction.
    # Alternatively, the LLM could return WRONG_JURISDICTION, but pre-filtering is safer.
    assert result.abstention_reason == AbstentionReason.NO_EVIDENCE
    assert result.strength == EvidenceStrength.INSUFFICIENT

@pytest.mark.asyncio
async def test_condition_missing_info(db_session: AsyncSession, corpus_dir: str):
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    # Trigger the mock LLM missing info
    result = await assess_query("Can I patent this magic unknown plant?", "india", db_session)
    assert result.abstention_reason == AbstentionReason.MISSING_INFO
    assert result.strength == EvidenceStrength.INSUFFICIENT
    assert result.clarifying_question is not None

@pytest.mark.asyncio
async def test_condition_conflicting_evidence(db_session: AsyncSession, corpus_dir: str):
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    result = await assess_query("Assess patent conflicting_trigger", "india", db_session)
    assert result.abstention_reason == AbstentionReason.CONFLICTING_EVIDENCE
    assert result.strength == EvidenceStrength.INSUFFICIENT

@pytest.mark.asyncio
async def test_condition_outdated_source(db_session: AsyncSession, corpus_dir: str):
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    result = await assess_query("Assess patent outdated_trigger", "india", db_session)
    assert result.abstention_reason == AbstentionReason.OUTDATED_SOURCE
    assert result.strength == EvidenceStrength.INSUFFICIENT

@pytest.mark.asyncio
async def test_successful_grounding(db_session: AsyncSession, corpus_dir: str):
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    result = await assess_query("computer programme", "india", db_session)
    
    assert result.abstention_reason == AbstentionReason.NONE
    assert result.strength == EvidenceStrength.STRONG
    assert len(result.claims) > 0
    assert result.claims[0].verified is True
    # The citation should match a real chunk ID
    assert len(result.claims[0].citations) > 0
    assert len(result.sources_used) > 0

@pytest.mark.asyncio
async def test_hallucinated_citation(db_session: AsyncSession, corpus_dir: str):
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    
    # We'll mock the LLM directly in this test to force a hallucinated citation
    from app.core import llm
    original_mock = llm._mock_generation
    
    def fake_mock_generation(prompt, model):
        from app.schemas.rag import IntentCategory, AbstentionReason, Claim
        return model(
            intent=IntentCategory.PATENT_ELIGIBILITY,
            abstention_reason=AbstentionReason.NONE,
            clarifying_question=None,
            claims=[
                Claim(text="Fake claim.", citations=["made-up-uuid-1234"], verified=False)
            ],
            summary="This citation is fake."
        )
        
    llm._mock_generation = fake_mock_generation
    try:
        result = await assess_query("computer programme", "india", db_session)
        assert result.strength == EvidenceStrength.WEAK
        assert len(result.claims) == 1
        assert result.claims[0].verified is False
        assert len(result.claims[0].citations) == 0  # Invalid citation stripped
    finally:
        llm._mock_generation = original_mock
