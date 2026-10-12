"""Automated tests for hybrid retrieval, chunking, and source metadata."""

import pytest
from app.retrieval.index import global_index
from app.retrieval.sources import build_citations


def test_relevant_retrieval_rahul_vohra():
    results = global_index.retrieve("How did Rahul Vohra measure PMF with the 40% benchmark?", top_k=2)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert "Rahul Vohra" in top_chunk.guest_name
    assert "Superhuman" in top_chunk.episode_title
    assert score >= 0.50

    citations = build_citations(results)
    assert len(citations) == len(results)
    assert citations[0].guest_name == "Rahul Vohra"
    assert len(citations[0].snippet) > 20


def test_relevant_retrieval_elena_verna():
    results = global_index.retrieve("What does Elena Verna recommend for onboarding and Time to Aha?", top_k=2)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert "Elena Verna" in top_chunk.guest_name
    assert "retention" in top_chunk.content.lower() or "aha" in top_chunk.content.lower()


def test_empty_retrieval_out_of_domain():
    results = global_index.retrieve("What is the recipe for baking a chocolate cake with sourdough?", top_k=3)
    # The hybrid index with threshold should yield zero chunks for completely unrelated domains
    assert len(results) == 0
