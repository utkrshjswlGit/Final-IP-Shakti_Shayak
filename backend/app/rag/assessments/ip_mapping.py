"""Intellectual Property Opportunity Mapping."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.domain import DomainResult, DomainState, ProductClassification, UserContext
from app.schemas.rag import EvidenceStrength, AbstentionReason
from app.rag.orchestration import assess_query

async def map_ip_opportunity(
    context: UserContext, 
    classification: ProductClassification, 
    db: AsyncSession
) -> DomainResult:
    """Assess patentability and IP opportunities."""
    
    # Check if it's purely traditional
    if classification.is_traditional_medicine and not "formulation" in classification.product_type.lower():
        # Known deterministic hurdle: raw traditional herbs are not patentable (Section 3(p)).
        query = f"Is the mere discovery of a naturally occurring herb like {', '.join(classification.key_ingredients)} patentable?"
        assessment = await assess_query(query, "india", db)
        
        return DomainResult(
            domain_name="IP_OPPORTUNITY",
            status=DomainState.NOT_IDENTIFIED,
            reasoning="Naturally occurring herbs and traditional knowledge are explicitly excluded from patentability. However, a novel, synergistic formulation might be patentable.",
            evidence=assessment.claims,
            confidence=assessment.strength,
            missing_information=["Details of any novel extraction process or synergistic formulation"],
            next_step="If you have created a novel formulation, provide specific ratios and clinical evidence of enhanced efficacy."
        )

    # General IP assessment
    query = f"What are the patentability criteria or exclusions for a {classification.product_type} containing {', '.join(classification.key_ingredients)}?"
    assessment = await assess_query(query, "india", db)
    
    if assessment.abstention_reason != AbstentionReason.NONE:
        return DomainResult(
            domain_name="IP_OPPORTUNITY",
            status=DomainState.INSUFFICIENT_EVIDENCE,
            reasoning="Could not confidently assess the IP opportunity. " + assessment.summary,
            evidence=[],
            confidence=EvidenceStrength.INSUFFICIENT,
            missing_information=[],
            next_step="Provide more technical details about the invention."
        )
        
    return DomainResult(
        domain_name="IP_OPPORTUNITY",
        status=DomainState.POTENTIALLY_RELEVANT,
        reasoning="The innovation may be eligible for patent protection provided it demonstrates novelty, inventive step, and industrial applicability, and does not fall under specific exclusions like Section 3(d) or 3(p).",
        evidence=assessment.claims,
        confidence=assessment.strength,
        missing_information=["Prior art search results", "Evidence of enhanced efficacy"],
        next_step="Conduct a formal prior art search to establish novelty."
    )
