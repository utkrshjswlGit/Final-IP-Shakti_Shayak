"""Main entry point orchestrating classification and routing to specific domains."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.domain import DomainResult, UserContext
from app.rag.classification import classify_product
from app.rag.assessments.abs_screening import screen_abs
from app.rag.assessments.ip_mapping import map_ip_opportunity

from app.rag.assessments.tk_assessment import assess_traditional_knowledge

async def execute_full_assessment(context: UserContext, db: AsyncSession) -> List[DomainResult]:
    """Classify the user input and route to relevant domain engines."""
    
    # 1. Product Classification
    classification = classify_product(context)
    
    # 2. Routing Logic
    results: List[DomainResult] = []
    
    # IP mapping
    ip_result = await map_ip_opportunity(context, classification, db)
    results.append(ip_result)
    
    # ABS screening
    abs_result = await screen_abs(context, classification, db)
    results.append(abs_result)
    
    # TK assessment
    tk_result = await assess_traditional_knowledge(context, classification, db)
    results.append(tk_result)
    
    return results
