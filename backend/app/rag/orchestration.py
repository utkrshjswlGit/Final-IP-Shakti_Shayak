"""RAG Orchestrator: retrieval, generation, citation verification, and abstention."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.retrieval import retrieve_evidence, RetrievedEvidence
from app.schemas.rag import GroundedAssessment, LLMStructuredOutput, AbstentionReason, EvidenceStrength, Claim
from app.core.llm import generate_structured_response
from app.core.logging import get_logger

logger = get_logger(__name__)

async def assess_query(query: str, jurisdiction: str, db: AsyncSession) -> GroundedAssessment:
    """Full RAG pipeline for authoritative IP/Regulatory assessment."""
    
    # 1. Retrieve Evidence
    evidence_list = await retrieve_evidence(query=query, jurisdiction=jurisdiction, db=db, top_k=5)
    
    # Check if empty (NO_EVIDENCE scenario)
    if not evidence_list:
        return GroundedAssessment(
            query=query,
            jurisdiction=jurisdiction,
            intent="unclear",
            strength=EvidenceStrength.INSUFFICIENT,
            abstention_reason=AbstentionReason.NO_EVIDENCE,
            clarifying_question=None,
            claims=[],
            summary="No relevant evidence found in the specified jurisdiction.",
            sources_used=[]
        )
        
    # 2. Context Construction
    context_blocks = []
    valid_chunk_ids = set()
    sources_used: Dict[str, Dict[str, str]] = {}
    
    for ev in evidence_list:
        valid_chunk_ids.add(ev.chunk.id)
        doc = ev.document
        sources_used[doc.id] = {
            "title": doc.title,
            "authority": doc.authority,
            "url": doc.source_url or "",
            "version": doc.version or ""
        }
        
        block = f"[{ev.chunk.id}] (Source: {doc.title}, {ev.chunk.hierarchy_level_1} > {ev.chunk.hierarchy_level_2})\n{ev.chunk.content}"
        context_blocks.append(block)
        
    context_str = "\n\n".join(context_blocks)
    
    # 3. LLM Prompt Construction
    prompt = f"""
You are a strict Ayurveda IP and Regulatory assistant.
Evaluate the following query against the provided evidence ONLY.
Never fabricate a citation. You must cite the [chunk-id] for every claim.

If the query is asking about a specific plant but doesn't provide enough details, abstain and ask for the scientific name.
If the evidence contradicts itself, abstain due to conflicting evidence.
If the evidence explicitly states it is outdated, abstain due to outdated source.

User Query: {query}
Jurisdiction: {jurisdiction}

Evidence:
{context_str}
"""
    
    # 4. Structured Generation
    llm_output: LLMStructuredOutput = generate_structured_response(prompt, LLMStructuredOutput)
    
    # 5. Abstention Evaluation
    if llm_output.abstention_reason != AbstentionReason.NONE:
        return GroundedAssessment(
            query=query,
            jurisdiction=jurisdiction,
            intent=llm_output.intent,
            strength=EvidenceStrength.INSUFFICIENT,
            abstention_reason=llm_output.abstention_reason,
            clarifying_question=llm_output.clarifying_question,
            claims=[],
            summary=llm_output.summary,
            sources_used=list(sources_used.values())
        )
        
    # 6. Citation Verification & Evidence Strength Calculation
    verified_claims = []
    all_citations_verified = True
    
    for claim in llm_output.claims:
        valid_citations_for_claim = []
        for cite in claim.citations:
            if cite in valid_chunk_ids:
                valid_citations_for_claim.append(cite)
            else:
                logger.warning("invalid_citation_hallucinated", cite=cite, claim=claim.text)
                
        # If the claim has at least one valid citation, keep it.
        # Otherwise, mark unverified. (If 0 citations supplied but required, it's also unverified)
        is_verified = len(valid_citations_for_claim) > 0 and len(valid_citations_for_claim) == len(claim.citations)
        if not is_verified:
            all_citations_verified = False
            
        verified_claims.append(Claim(
            text=claim.text,
            citations=valid_citations_for_claim,
            verified=is_verified
        ))
        
    # Calculate overall strength
    if not verified_claims:
        strength = EvidenceStrength.INSUFFICIENT
        abstention_reason = AbstentionReason.NO_EVIDENCE
        summary = "Could not verify any claims against the provided evidence."
    elif all_citations_verified:
        # In a real app, we'd check if any Tier 1 sources were cited. 
        # For now, if all citations strictly match context, it's STRONG.
        strength = EvidenceStrength.STRONG
        abstention_reason = AbstentionReason.NONE
        summary = llm_output.summary
    else:
        strength = EvidenceStrength.WEAK
        abstention_reason = AbstentionReason.NONE
        summary = llm_output.summary + " (Warning: Some claims could not be strictly verified.)"

    return GroundedAssessment(
        query=query,
        jurisdiction=jurisdiction,
        intent=llm_output.intent,
        strength=strength,
        abstention_reason=abstention_reason,
        clarifying_question=llm_output.clarifying_question,
        claims=verified_claims,
        summary=summary,
        sources_used=list(sources_used.values())
    )
