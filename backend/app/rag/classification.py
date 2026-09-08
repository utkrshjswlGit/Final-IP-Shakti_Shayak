"""Product classification engine combining deterministic rules and LLM extraction."""

import re
from typing import List
from app.schemas.domain import ProductClassification, UserContext
from app.core.llm import generate_structured_response

# A small deterministic dictionary for Ayurvedic keywords
AYURVEDA_KEYWORDS = [
    "ashwagandha", "tulsi", "neem", "turmeric", "haldi", "brahmi", 
    "triphala", "amla", "guggul", "shatavari", "giloy"
]

def classify_product(user_context: UserContext) -> ProductClassification:
    """Classify the innovation using rules and LLM structured extraction."""
    description_lower = user_context.description.lower()
    
    # 1. Deterministic Rule: Check for traditional herbs
    found_herbs = [herb for herb in AYURVEDA_KEYWORDS if herb in description_lower]
    
    # 2. Deterministic Rule: Foreign involvement
    has_foreign = False
    if user_context.citizenship.lower() != "india":
        has_foreign = True
    if "international" in [m.lower() for m in user_context.target_markets]:
        has_foreign = True
        
    # 3. LLM Extraction (to catch nuanced product types and complex formulations)
    prompt = f"""
    Analyze the following product/innovation description and classify it.
    Extract any key ingredients. Determine if it's a botanical, formulation, device, or process.
    
    Description: {user_context.description}
    """
    
    # Normally we would use the LLM to get the base schema
    # For robust deterministic fallback or mock scenarios:
    try:
        llm_class: ProductClassification = generate_structured_response(prompt, ProductClassification)
        # Merge deterministic findings
        llm_class.has_foreign_involvement = has_foreign or llm_class.has_foreign_involvement
        if found_herbs:
            llm_class.is_traditional_medicine = True
            # Merge lists uniquely
            llm_class.key_ingredients = list(set(llm_class.key_ingredients + found_herbs))
        return llm_class
    except Exception:
        # Fallback if LLM fails
        return ProductClassification(
            product_type="formulation" if "formulation" in description_lower else "unknown",
            key_ingredients=found_herbs,
            is_traditional_medicine=bool(found_herbs),
            has_foreign_involvement=has_foreign
        )
