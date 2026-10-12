"""Citation builder and source provenance tracker."""

import uuid
from typing import List, Tuple
from app.retrieval.chunker import TranscriptChunk
from app.schemas.session import CitationSchema


def build_citations(retrieved_chunks: List[Tuple[TranscriptChunk, float]]) -> List[CitationSchema]:
    """Converts retrieved chunks into structured citation objects."""
    citations: List[CitationSchema] = []

    for chunk, score in retrieved_chunks:
        # Create a representative snippet (first ~250 characters)
        cleaned_content = " ".join(chunk.content.split())
        snippet = cleaned_content[:280] + ("..." if len(cleaned_content) > 280 else "")

        citation = CitationSchema(
            id=str(uuid.uuid4()),
            episode_title=chunk.episode_title,
            guest_name=chunk.guest_name,
            source_url=chunk.source_url,
            chunk_id=chunk.chunk_id,
            similarity_score=round(score, 3),
            snippet=snippet,
        )
        citations.append(citation)

    return citations
