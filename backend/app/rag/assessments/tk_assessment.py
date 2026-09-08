"""Traditional Knowledge (TK) Assessment."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.domain import DomainResult, DomainState, ProductClassification, UserContext
from app.schemas.rag import EvidenceStrength, AbstentionReason
from app.rag.orchestration import assess_query

async def assess_traditional_knowledge(
    context: UserContext, 
    classification: ProductClassification, 
    db: AsyncSession
) -> DomainResult:
    """Assess whether the product utilizes Traditional Knowledge and intersects with TKDL/Guidelines."""
    
    if not classification.is_traditional_medicine:
        return DomainResult(
            domain_name="TRADITIONAL_KNOWLEDGE",
            status=DomainState.NOT_IDENTIFIED,
            reasoning="The product description does not contain recognized traditional herbs or frameworks.",
            evidence=[],
            confidence=EvidenceStrength.STRONG, # Confident it's not traditional based on description
            missing_information=[],
            next_step="Proceed with standard IP mapping. If traditional components exist, please list them."
        )

    # General TK assessment query
    query = f"How does the traditional knowledge framework apply to {', '.join(classification.key_ingredients)} regarding documentation or prior art?"
    assessment = await assess_query(query, "india", db)
    
    if assessment.abstention_reason != AbstentionReason.NONE:
        return DomainResult(
            domain_name="TRADITIONAL_KNOWLEDGE",
            status=DomainState.INSUFFICIENT_EVIDENCE,
            reasoning="Could not confidently assess the TK implications. " + assessment.summary,
            evidence=[],
            confidence=EvidenceStrength.INSUFFICIENT,
            missing_information=["Specific traditional texts referenced", "Method of procurement"],
            next_step="Consult the Traditional Knowledge Digital Library (TKDL) directly."
        )
        
    return DomainResult(
        domain_name="TRADITIONAL_KNOWLEDGE",
        status=DomainState.POTENTIALLY_RELEVANT,
        reasoning="The ingredients listed are associated with traditional medicine. Formulations based on these may face patentability hurdles under Section 3(p) unless they show synergistic effects. They also may be documented in the TKDL.",
        evidence=assessment.claims,
        confidence=assessment.strength,
        missing_information=["Exact proportions of the formulation", "Evidence of synergistic properties"],
        next_step="Ensure any patent claims clearly differentiate from prior traditional use and demonstrate novel synergistic efficacy."
    )
