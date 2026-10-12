"""Ingestion pipeline for loading transcripts into the hybrid index."""

import json
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.retrieval.chunker import chunk_transcript, TranscriptChunk
from app.retrieval.index import global_index


def load_transcript_file(file_path: Path) -> Dict[str, Any]:
    """Loads a single JSON or Markdown transcript file."""
    if file_path.suffix.lower() == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif file_path.suffix.lower() in [".md", ".txt"]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        stem = file_path.stem
        return {
            "episode_id": stem,
            "episode_title": stem.replace("_", " ").title(),
            "guest_name": "Lenny's Guest",
            "source_url": "",
            "transcript": content,
        }
    return {}


def run_ingestion(custom_dirs: List[Path] = None) -> Dict[str, Any]:
    """Scans directories, extracts chunks, and loads the hybrid index."""
    search_dirs = custom_dirs or [
        Path(settings.FIXTURES_DIR),
        Path(settings.DATA_DIR) / "raw",
        Path(settings.DATA_DIR) / "processed",
    ]

    all_chunks: List[TranscriptChunk] = []
    loaded_episodes = 0

    for d in search_dirs:
        if not d.exists():
            continue
        for file_path in d.glob("*.*"):
            if file_path.suffix.lower() in [".json", ".md", ".txt"]:
                try:
                    doc = load_transcript_file(file_path)
                    if doc and "transcript" in doc and doc["transcript"].strip():
                        chunks = chunk_transcript(doc)
                        all_chunks.extend(chunks)
                        loaded_episodes += 1
                        logger.debug(f"Loaded {len(chunks)} chunks from {file_path.name}")
                except Exception as exc:
                    logger.error(f"Error loading transcript {file_path}: {exc}")

    global_index.build_index(all_chunks)

    stats = {
        "episodes_loaded": loaded_episodes,
        "chunks_indexed": len(all_chunks),
        "status": "ready" if all_chunks else "empty",
    }
    logger.info("Transcript ingestion complete", extra=stats)
    return stats
