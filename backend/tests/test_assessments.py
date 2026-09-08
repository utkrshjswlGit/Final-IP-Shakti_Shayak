"""Integration tests for domain-specific assessments."""

import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.ingestion import ingest_markdown_document
from app.schemas.domain import UserContext, DomainState
from app.rag.classification import classify_product
from app.rag.routing import execute_full_assessment

@pytest.fixture
def corpus_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(current_dir), "corpus")

def test_product_classification_deterministic():
    """Test deterministic rule-based classification."""
    context = UserContext(
        description="A novel formulation of ashwagandha and neem.",
        citizenship="USA"
    )
    classification = classify_product(context)
    
    # Deterministic checks
    assert classification.is_traditional_medicine is True
    assert "ashwagandha" in classification.key_ingredients
    assert "neem" in classification.key_ingredients
    # Because citizenship is USA
    assert classification.has_foreign_involvement is True

@pytest.mark.asyncio
async def test_abs_screening_deterministic_foreigner(db_session: AsyncSession, corpus_dir: str):
    """Test that a foreigner immediately gets routed to REVIEW status for ABS."""
    await ingest_markdown_document(os.path.join(corpus_dir, "bd_act_2002.md"), db_session)
    
    context = UserContext(
        description="Ashwagandha root extraction for export.",
        citizenship="USA"
    )
    
    # execute_full_assessment calls classification and runs both engines
    results = await execute_full_assessment(context, db_session)
    
    abs_result = next(r for r in results if r.domain_name == "ABS_SCREENING")
    assert abs_result.status == DomainState.REVIEW
    assert "non-citizen" in abs_result.reasoning.lower()

@pytest.mark.asyncio
async def test_ip_opportunity_traditional_medicine(db_session: AsyncSession, corpus_dir: str):
    """Test that purely traditional herbs get NOT_IDENTIFIED for IP opportunity to avoid yes/no legal trap."""
    await ingest_markdown_document(os.path.join(corpus_dir, "patents_act_1970.md"), db_session)
    
    # "botanical" without "formulation" triggers the deterministic IP check for pure traditional knowledge
    context = UserContext(
        description="I discovered that ashwagandha is good for health.",
        citizenship="india"
    )
    # Patch the LLM classification mock to ensure it returns 'botanical' product type
    # Actually, our fallback returns 'unknown' if 'formulation' isn't in string
    # Let's see what classify_product returns naturally
    
    results = await execute_full_assessment(context, db_session)
    ip_result = next(r for r in results if r.domain_name == "IP_OPPORTUNITY")
    
    assert ip_result.status == DomainState.NOT_IDENTIFIED
    assert "naturally occurring" in ip_result.reasoning.lower()
    assert "novel formulation" in ip_result.next_step.lower()

@pytest.mark.asyncio
async def test_tk_assessment_not_identified(db_session: AsyncSession, corpus_dir: str):
    """Test that a non-traditional product bypasses the TK engine."""
    context = UserContext(
        description="A completely synthetic chemical polymer for generic pharma.",
        citizenship="india"
    )
    results = await execute_full_assessment(context, db_session)
    tk_result = next(r for r in results if r.domain_name == "TRADITIONAL_KNOWLEDGE")
    
    assert tk_result.status == DomainState.NOT_IDENTIFIED
    assert "not contain recognized traditional herbs" in tk_result.reasoning.lower()
