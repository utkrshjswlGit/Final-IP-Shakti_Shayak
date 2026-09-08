"""Knowledge base ingestion pipeline."""

import hashlib
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentChunk
from app.rag.chunking import parse_markdown_document
from app.core.llm import get_embeddings
from app.core.logging import get_logger

logger = get_logger(__name__)

async def ingest_markdown_document(filepath: str, db: AsyncSession) -> Optional[Document]:
    """Parse, chunk, embed, and store a markdown document."""
    
    parsed = parse_markdown_document(filepath)
    meta = parsed.metadata
    
    if not meta.get("title") or not meta.get("authority"):
        logger.error("ingest_failed_missing_metadata", filepath=filepath)
        return None
        
    # Generate content hash to avoid duplicate ingestion
    with open(filepath, 'r', encoding='utf-8') as f:
        content_hash = hashlib.sha256(f.read().encode("utf-8")).hexdigest()
        
    # Check if already exists
    existing = await db.execute(select(Document).where(Document.content_hash == content_hash))
    if existing.scalar_one_or_none():
        logger.info("ingest_skipped_duplicate", title=meta["title"])
        return None

    doc = Document(
        title=meta["title"],
        authority=meta["authority"],
        jurisdiction=meta["jurisdiction"],
        domain=meta["domain"],
        document_type=meta["document_type"],
        version=meta.get("version"),
        publication_date=meta.get("publication_date"),
        effective_date=meta.get("effective_date"),
        status=meta.get("status", "active"),
        source_url=meta.get("source_url"),
        content_hash=content_hash,
        trust_tier=meta.get("trust_tier", 2),
        language=meta.get("language", "en")
    )
    
    db.add(doc)
    await db.flush() # To get doc.id generated
    
    # Generate embeddings in batch
    texts_to_embed = [
        # Prepend hierarchy context to the text for better embedding semantics
        f"{c.h1 or ''} > {c.h2 or ''}\n{c.content}"
        for c in parsed.chunks
    ]
    
    embeddings = get_embeddings(texts_to_embed)
    
    for i, chunk_dto in enumerate(parsed.chunks):
        chunk = DocumentChunk(
            document_id=doc.id,
            content=chunk_dto.content,
            hierarchy_level_1=chunk_dto.h1,
            hierarchy_level_2=chunk_dto.h2,
            hierarchy_level_3=chunk_dto.h3,
            char_start=chunk_dto.char_start,
            char_end=chunk_dto.char_end,
            embedding=embeddings[i]
        )
        db.add(chunk)
        
    logger.info("ingest_success", title=doc.title, chunks=len(parsed.chunks))
    return doc
