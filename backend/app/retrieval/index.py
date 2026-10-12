"""Hybrid retrieval index combining lexical BM25 and vector TF-IDF scoring."""

import math
import re
from typing import List, Dict, Any, Tuple
from app.core.logging import logger
from app.retrieval.chunker import TranscriptChunk


def tokenize(text: str) -> List[str]:
    """Basic lowercased alphanumeric tokenizer with stopword suppression."""
    tokens = re.findall(r"\b[a-zA-Z0-9_\-\$]{2,}\b", text.lower())
    stopwords = {
        "the", "and", "is", "in", "to", "of", "it", "that", "you", "we", "for",
        "on", "are", "as", "with", "at", "be", "this", "have", "from", "or",
        "an", "by", "not", "but", "what", "all", "were", "when", "can", "said",
        "there", "use", "so", "up", "out", "about", "who", "which", "go", "me",
    }
    return [t for t in tokens if t not in stopwords]


class HybridRetrievalIndex:
    def __init__(self):
        self.chunks: List[TranscriptChunk] = []
        self.doc_count = 0
        self.avg_doc_len = 0.0
        self.inverted_index: Dict[str, List[Tuple[int, int]]] = {}  # term -> [(chunk_idx, count)]
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.doc_magnitudes: List[float] = []
        self.idf: Dict[str, float] = {}

    def build_index(self, chunks: List[TranscriptChunk]):
        """Builds lexical and vector indices from chunks."""
        self.chunks = chunks
        self.doc_count = len(chunks)
        self.inverted_index.clear()
        self.doc_term_freqs.clear()
        self.doc_magnitudes.clear()
        self.idf.clear()

        if self.doc_count == 0:
            logger.warning("Empty chunk list provided to HybridRetrievalIndex")
            return

        total_words = 0
        doc_frequencies: Dict[str, int] = {}

        for idx, chunk in enumerate(chunks):
            # Include guest name and episode title in token stream to boost metadata matches
            full_text = f"{chunk.guest_name} {chunk.episode_title} {chunk.content}"
            tokens = tokenize(full_text)
            total_words += len(tokens)

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            self.doc_term_freqs.append(tf)

            for term, count in tf.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append((idx, count))
                doc_frequencies[term] = doc_frequencies.get(term, 0) + 1

        self.avg_doc_len = total_words / self.doc_count if self.doc_count > 0 else 1.0

        # Compute IDF
        for term, df in doc_frequencies.items():
            self.idf[term] = math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))

        # Compute vector magnitudes for cosine similarity
        for tf in self.doc_term_freqs:
            mag_sq = 0.0
            for term, count in tf.items():
                weight = (1.0 + math.log(count)) * self.idf.get(term, 0.0)
                mag_sq += weight * weight
            self.doc_magnitudes.append(math.sqrt(mag_sq) if mag_sq > 0 else 1.0)

        logger.info(
            f"Successfully indexed {self.doc_count} transcript chunks across {len(self.idf)} unique terms",
            extra={"chunks_count": self.doc_count, "terms_count": len(self.idf)},
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.40,
    ) -> List[Tuple[TranscriptChunk, float]]:
        """Retrieves top-k most relevant chunks using hybrid lexical & semantic scoring."""
        if self.doc_count == 0:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_tf: Dict[str, int] = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        # Query vector magnitude
        q_mag_sq = 0.0
        for term, count in query_tf.items():
            weight = (1.0 + math.log(count)) * self.idf.get(term, 0.0)
            q_mag_sq += weight * weight
        q_mag = math.sqrt(q_mag_sq) if q_mag_sq > 0 else 1.0

        # Score all candidate documents
        bm25_scores: Dict[int, float] = {}
        cos_scores: Dict[int, float] = {}
        k1 = 1.5
        b = 0.75

        # Check for exact guest name mentions in query
        lower_query = query.lower()
        guest_boost: Dict[int, float] = {}
        for idx, chunk in enumerate(self.chunks):
            if chunk.guest_name.lower() in lower_query:
                guest_boost[idx] = 0.35

        for term in query_tf:
            if term not in self.inverted_index:
                continue
            term_idf = self.idf[term]
            q_weight = (1.0 + math.log(query_tf[term])) * term_idf

            for doc_idx, count in self.inverted_index[term]:
                doc_len = len(self.doc_term_freqs[doc_idx])
                # BM25 component
                tf_norm = (count * (k1 + 1)) / (count + k1 * (1 - b + b * (doc_len / self.avg_doc_len)))
                bm25_scores[doc_idx] = bm25_scores.get(doc_idx, 0.0) + (term_idf * tf_norm)

                # Vector dot product
                doc_weight = (1.0 + math.log(count)) * term_idf
                cos_scores[doc_idx] = cos_scores.get(doc_idx, 0.0) + (q_weight * doc_weight)

        # Normalize and combine scores
        candidate_scores: List[Tuple[int, float]] = []
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        if max_bm25 <= 0:
            max_bm25 = 1.0

        for doc_idx in set(bm25_scores.keys()).union(set(cos_scores.keys())):
            norm_bm25 = bm25_scores.get(doc_idx, 0.0) / max_bm25
            norm_cos = cos_scores.get(doc_idx, 0.0) / (q_mag * self.doc_magnitudes[doc_idx])
            boost = guest_boost.get(doc_idx, 0.0)

            # Combined hybrid formula
            final_score = (0.50 * norm_cos) + (0.50 * norm_bm25) + boost
            final_score = min(1.0, final_score)

            if final_score >= similarity_threshold:
                candidate_scores.append((doc_idx, final_score))

        # Sort descending by score
        candidate_scores.sort(key=lambda x: x[1], reverse=True)

        results: List[Tuple[TranscriptChunk, float]] = []
        for doc_idx, score in candidate_scores[:top_k]:
            results.append((self.chunks[doc_idx], score))

        return results


# Global singleton index
global_index = HybridRetrievalIndex()
