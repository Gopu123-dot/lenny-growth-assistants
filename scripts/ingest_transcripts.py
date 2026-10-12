"""CLI script for ingesting transcripts and printing index diagnostics."""

import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.retrieval.ingest import run_ingestion
from app.retrieval.index import global_index


def main():
    print("=" * 60)
    print("Ingesting Lenny's Podcast Transcripts into Hybrid Index")
    print("=" * 60)

    stats = run_ingestion()
    print(f"Status:          {stats['status']}")
    print(f"Episodes loaded: {stats['episodes_loaded']}")
    print(f"Chunks indexed:  {stats['chunks_indexed']}")
    print("-" * 60)

    # Perform a test retrieval query
    test_query = "What did Rahul Vohra say about the 40% product-market fit engine?"
    print(f"Testing retrieval for: '{test_query}'")
    results = global_index.retrieve(test_query, top_k=2)

    if results:
        print(f"Found {len(results)} matching chunks:")
        for idx, (chunk, score) in enumerate(results, 1):
            print(f"  [{idx}] Episode: {chunk.episode_title} ({chunk.guest_name})")
            print(f"      Score:   {score:.3f}")
            print(f"      Snippet: {chunk.content[:140]}...\n")
    else:
        print("Warning: No chunks retrieved.")

    print("Ingestion verification completed successfully.")


if __name__ == "__main__":
    main()
