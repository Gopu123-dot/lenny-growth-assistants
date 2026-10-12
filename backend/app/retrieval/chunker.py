"""Transcript chunker preserving paragraph integrity and metadata."""

import re
from typing import List, Dict, Any


class TranscriptChunk:
    def __init__(
        self,
        chunk_id: str,
        episode_id: str,
        episode_title: str,
        guest_name: str,
        source_url: str,
        content: str,
        chunk_index: int,
        word_count: int,
        approx_tokens: int,
    ):
        self.chunk_id = chunk_id
        self.episode_id = episode_id
        self.episode_title = episode_title
        self.guest_name = guest_name
        self.source_url = source_url
        self.content = content
        self.chunk_index = chunk_index
        self.word_count = word_count
        self.approx_tokens = approx_tokens

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "episode_id": self.episode_id,
            "episode_title": self.episode_title,
            "guest_name": self.guest_name,
            "source_url": self.source_url,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "word_count": self.word_count,
            "approx_tokens": self.approx_tokens,
        }


def chunk_transcript(
    doc: Dict[str, Any],
    target_words: int = 250,
    overlap_words: int = 40,
) -> List[TranscriptChunk]:
    """Splits a transcript document into structured chunks at conversational turn or paragraph boundaries."""
    transcript_text = doc.get("transcript", "")
    episode_id = doc.get("episode_id", "unknown_ep")
    episode_title = doc.get("episode_title", "Lenny's Podcast")
    guest_name = doc.get("guest_name", "Guest")
    source_url = doc.get("source_url", "")

    # Split by double newlines or speaker turn markers
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", transcript_text) if p.strip()]

    chunks: List[TranscriptChunk] = []
    current_paragraphs: List[str] = []
    current_words = 0
    chunk_idx = 0

    for para in paragraphs:
        para_word_count = len(para.split())
        if current_words + para_word_count > target_words and current_paragraphs:
            # Consolidate current chunk
            combined_text = "\n\n".join(current_paragraphs)
            w_count = len(combined_text.split())
            chunk_obj = TranscriptChunk(
                chunk_id=f"{episode_id}_chunk_{chunk_idx:03d}",
                episode_id=episode_id,
                episode_title=episode_title,
                guest_name=guest_name,
                source_url=source_url,
                content=combined_text,
                chunk_index=chunk_idx,
                word_count=w_count,
                approx_tokens=int(w_count * 1.33),
            )
            chunks.append(chunk_obj)
            chunk_idx += 1

            # Keep last paragraph for overlap continuity if feasible
            if len(current_paragraphs) > 1 and len(current_paragraphs[-1].split()) <= overlap_words:
                current_paragraphs = [current_paragraphs[-1], para]
                current_words = len(current_paragraphs[0].split()) + para_word_count
            else:
                current_paragraphs = [para]
                current_words = para_word_count
        else:
            current_paragraphs.append(para)
            current_words += para_word_count

    # Add trailing chunk
    if current_paragraphs:
        combined_text = "\n\n".join(current_paragraphs)
        w_count = len(combined_text.split())
        chunk_obj = TranscriptChunk(
            chunk_id=f"{episode_id}_chunk_{chunk_idx:03d}",
            episode_id=episode_id,
            episode_title=episode_title,
            guest_name=guest_name,
            source_url=source_url,
            content=combined_text,
            chunk_index=chunk_idx,
            word_count=w_count,
            approx_tokens=int(w_count * 1.33),
        )
        chunks.append(chunk_obj)

    return chunks
