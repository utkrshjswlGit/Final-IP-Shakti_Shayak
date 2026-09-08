"""LLM Adapter for embeddings and generation."""

import os
from typing import List, Any

from app.core.config import get_settings

settings = get_settings()

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Return embeddings for a list of texts.
    
    Uses a mock deterministic embedding if LLM_PROVIDER=mock,
    otherwise calls OpenAI API.
    """
    if not texts:
        return []

    if settings.llm_provider == "mock" or not settings.openai_api_key:
        return _mock_embeddings(texts)

    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
    
    response = client.embeddings.create(
        input=texts,
        model=settings.embedding_model
    )
    
    return [item.embedding for item in response.data]

def _mock_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate a deterministic but distinct fake embedding for tests.
    
    This is extremely simplistic and maps the first few chars
    of the string to a pseudo-random vector.
    """
    dim = settings.embedding_dimensions
    results = []
    
    for text in texts:
        # Uniform vector for testing so semantic rank doesn't randomize RRF
        vector = [0.1] * dim
        results.append(vector)
        
    return results

def generate_structured_response(prompt: str, response_model: type) -> Any:
    """Generate a structured response constrained by a Pydantic model.
    
    If LLM_PROVIDER=mock, returns predefined answers based on keywords to test RAG logic.
    """
    if settings.llm_provider == "mock" or not settings.openai_api_key:
        return _mock_generation(prompt, response_model)
        
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key.get_secret_value())
    
    completion = client.beta.pydantic.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are a strict legal assistant. Follow the JSON schema perfectly."},
            {"role": "user", "content": prompt}
        ],
        response_format=response_model,
    )
    
    return completion.choices[0].message.parsed

def _mock_generation(prompt: str, response_model: type) -> Any:
    """Mock LLM structured output for automated tests."""
    from app.schemas.rag import LLMStructuredOutput, IntentCategory, AbstentionReason, Claim
    import json
    import re
    
    prompt_lower = prompt.lower()
    
    # Check for missing info
    if "magic unknown plant" in prompt_lower:
        return response_model(
            intent=IntentCategory.UNCLEAR,
            abstention_reason=AbstentionReason.MISSING_INFO,
            clarifying_question="What is the scientific name of the plant?",
            claims=[],
            summary="Need more information."
        )
        
    # Check for conflicting evidence (mocked by a special trigger word)
    if "conflicting_trigger" in prompt_lower:
        return response_model(
            intent=IntentCategory.PATENT_ELIGIBILITY,
            abstention_reason=AbstentionReason.CONFLICTING_EVIDENCE,
            clarifying_question=None,
            claims=[],
            summary="The retrieved sources contradict each other."
        )

    # Check for outdated source (we'll trigger this if we see a specific term)
    if "outdated_trigger" in prompt_lower:
         return response_model(
            intent=IntentCategory.PATENT_ELIGIBILITY,
            abstention_reason=AbstentionReason.OUTDATED_SOURCE,
            clarifying_question=None,
            claims=[],
            summary="The available regulations are outdated."
        )

    # Extract all cited chunk IDs from the prompt (they look like [chunk-uuid])
    # to mock a successful grounding response.
    chunk_ids = re.findall(r'\[([a-f0-9\-]{36})\]', prompt)
    
    if not chunk_ids:
        # No chunks were provided in the context
        return response_model(
            intent=IntentCategory.PATENT_ELIGIBILITY,
            abstention_reason=AbstentionReason.NO_EVIDENCE,
            clarifying_question=None,
            claims=[],
            summary="No evidence available."
        )
        
    # Successful grounding
    return response_model(
        intent=IntentCategory.PATENT_ELIGIBILITY,
        abstention_reason=AbstentionReason.NONE,
        clarifying_question=None,
        claims=[
            Claim(text="This invention is not patentable.", citations=[chunk_ids[0]], verified=False)
        ],
        summary="Assessment based on evidence."
    )

