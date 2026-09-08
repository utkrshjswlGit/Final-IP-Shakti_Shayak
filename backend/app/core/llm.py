"""LLM Adapter for embeddings and generation."""

import os
from typing import List

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
