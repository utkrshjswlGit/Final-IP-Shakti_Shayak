"""Structure-aware markdown parser and chunker."""

import re
import yaml
from typing import Dict, Any, List

class DocumentChunkDTO:
    def __init__(
        self,
        content: str,
        h1: str = None,
        h2: str = None,
        h3: str = None,
        char_start: int = 0,
        char_end: int = 0
    ):
        self.content = content
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.char_start = char_start
        self.char_end = char_end

class ParsedDocument:
    def __init__(self, metadata: Dict[str, Any], chunks: List[DocumentChunkDTO]):
        self.metadata = metadata
        self.chunks = chunks

def parse_markdown_document(filepath: str) -> ParsedDocument:
    """Read a markdown file with YAML frontmatter, split into sections."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract YAML frontmatter
    metadata = {}
    content_text = text
    
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if frontmatter_match:
        frontmatter_str = frontmatter_match.group(1)
        metadata = yaml.safe_load(frontmatter_str) or {}
        content_text = text[frontmatter_match.end():]
        content_start_offset = frontmatter_match.end()
    else:
        content_start_offset = 0

    # We do a simplistic header split. Real production would use langchain or unstructured.
    # We'll split by lines and keep track of current H1, H2, H3.
    lines = content_text.split('\n')
    
    chunks = []
    
    current_h1 = None
    current_h2 = None
    current_h3 = None
    
    current_chunk_lines = []
    current_chunk_start_char = content_start_offset
    current_char_offset = content_start_offset
    
    def flush_chunk():
        if current_chunk_lines:
            chunk_text = "\n".join(current_chunk_lines).strip()
            if chunk_text:
                chunks.append(DocumentChunkDTO(
                    content=chunk_text,
                    h1=current_h1,
                    h2=current_h2,
                    h3=current_h3,
                    char_start=current_chunk_start_char,
                    char_end=current_char_offset
                ))
            current_chunk_lines.clear()

    for line in lines:
        line_len = len(line) + 1  # +1 for newline
        
        # Check for headers
        h1_match = re.match(r'^#\s+(.*)', line)
        h2_match = re.match(r'^##\s+(.*)', line)
        h3_match = re.match(r'^###\s+(.*)', line)
        
        if h1_match:
            flush_chunk()
            current_h1 = h1_match.group(1).strip()
            current_h2 = None
            current_h3 = None
            current_chunk_start_char = current_char_offset
            # Include the header in the chunk content for context
            current_chunk_lines.append(line)
        elif h2_match:
            flush_chunk()
            current_h2 = h2_match.group(1).strip()
            current_h3 = None
            current_chunk_start_char = current_char_offset
            current_chunk_lines.append(line)
        elif h3_match:
            flush_chunk()
            current_h3 = h3_match.group(1).strip()
            current_chunk_start_char = current_char_offset
            current_chunk_lines.append(line)
        else:
            current_chunk_lines.append(line)
            
        current_char_offset += line_len
        
    flush_chunk()
    
    return ParsedDocument(metadata=metadata, chunks=chunks)
