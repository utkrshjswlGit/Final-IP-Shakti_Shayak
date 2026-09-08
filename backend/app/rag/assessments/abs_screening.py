"""Access & Benefit Sharing (ABS) Screening."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.domain import DomainResult, DomainState, ProductClassification, UserContext
from app.schemas.rag import EvidenceStrength
from app.rag.orchestration import assess_query

async def screen_abs(
    context: UserContext, 
    classification: ProductClassification, 
    db: AsyncSession
) -> DomainResult:
    """Assess if the innovation requires NBA approval under the Biological Diversity Act."""
    
    # 1. Deterministic Screening
    if context.citizenship.lower() != "india" or classification.has_foreign_involvement:
        # We know deterministic rules state foreign entities need NBA approval (Section 3).
        # We still run RAG to provide the exact cited law.
        query = "Do non-citizens or foreign entities require approval from the National Biodiversity Authority for research or commercial utilization of biological resources?"
        assessment = await assess_query(query, "india", db)
        
        return DomainResult(
            domain_name="ABS_SCREENING",
            status=DomainState.REVIEW,
            reasoning="As a non-citizen or foreign-involved entity, strict regulatory approval is required from the National Biodiversity Authority prior to utilizing Indian biological resources.",
            evidence=assessment.claims,
            confidence=assessment.strength,
            missing_information=[],
            next_step="Consult legal counsel and prepare an application to the National Biodiversity Authority."
        )

    # 2. General Screening
    query = f"Does the research or commercial utilization of {', '.join(classification.key_ingredients)} by an Indian citizen require NBA approval or State Biodiversity Board intimation?"
    assessment = await assess_query(query, "india", db)
    
    if assessment.strength == EvidenceStrength.INSUFFICIENT:
         return DomainResult(
            domain_name="ABS_SCREENING",
            status=DomainState.INSUFFICIENT_EVIDENCE,
            reasoning="Could not find sufficient evidence regarding ABS rules for this specific scenario.",
            evidence=[],
            confidence=EvidenceStrength.INSUFFICIENT,
            missing_information=["Specific formulation processes", "Source of biological material procurement"],
            next_step="Provide more details regarding how and where the biological materials were sourced."
        )

    # If evidence found, we defer to POTENTIALLY_RELEVANT rather than a hard "Supported"
    # because ABS is complex and we don't produce yes/no legal conclusions.
    return DomainResult(
        domain_name="ABS_SCREENING",
        status=DomainState.POTENTIALLY_RELEVANT,
        reasoning="Access to biological resources generally requires compliance with the Biological Diversity Act. An Indian entity typically requires prior intimation to the State Biodiversity Board for commercial utilization.",
        evidence=assessment.claims,
        confidence=assessment.strength,
        missing_information=[],
        next_step="Verify if your activities constitute 'commercial utilization' and submit intimation to the relevant State Biodiversity Board."
    )
