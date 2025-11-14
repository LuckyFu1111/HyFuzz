"""
Semantic Cache for LLM Responses

Implements semantic similarity-based caching to reduce LLM API calls
by matching similar prompts instead of exact matches.

Features:
- Embedding-based semantic similarity
- Configurable similarity threshold
- Multi-tier caching (exact, semantic, persistent)
- Automatic cache warming
- Hit rate tracking

Author: HyFuzz Team
Version: 1.0.0
Date: 2025-01-13
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class CachedResponse:
    """Cached LLM response with metadata"""
    prompt: str
    response: str
    embedding: Optional[np.ndarray] = None
    prompt_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    token_count: int = 0
    response_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.prompt_hash:
            self.prompt_hash = hashlib.sha256(self.prompt.encode()).hexdigest()

    def update_access(self):
        """Update access statistics"""
        self.accessed_at = datetime.now()
        self.access_count += 1

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if entry is expired"""
        if ttl_seconds <= 0:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > ttl_seconds


@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_requests: int = 0
    exact_hits: int = 0
    semantic_hits: int = 0
    misses: int = 0
    total_tokens_saved: int = 0
    total_time_saved_ms: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Overall cache hit rate"""
        total = self.total_requests
        if total == 0:
            return 0.0
        return (self.exact_hits + self.semantic_hits) / total

    @property
    def semantic_hit_rate(self) -> float:
        """Semantic-only hit rate"""
        total = self.total_requests - self.exact_hits
        if total == 0:
            return 0.0
        return self.semantic_hits / total

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_requests": self.total_requests,
            "exact_hits": self.exact_hits,
            "semantic_hits": self.semantic_hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate * 100:.2f}%",
            "semantic_hit_rate": f"{self.semantic_hit_rate * 100:.2f}%",
            "tokens_saved": self.total_tokens_saved,
            "time_saved_ms": round(self.total_time_saved_ms, 2)
        }


# ==============================================================================
# SEMANTIC CACHE
# ==============================================================================

class SemanticCache:
    """
    Semantic similarity-based cache for LLM responses

    Uses embeddings to find semantically similar prompts and return
    cached responses, significantly reducing LLM API calls.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        max_cache_size: int = 10000,
        ttl_seconds: int = 3600,
        embedding_model: str = "simple",
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize semantic cache

        Args:
            similarity_threshold: Minimum cosine similarity for cache hit (0.0-1.0)
            max_cache_size: Maximum number of cached entries
            ttl_seconds: Time-to-live for cache entries
            embedding_model: Embedding model to use ('simple', 'sentence-transformers')
            cache_dir: Directory for persistent cache
        """
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_seconds
        self.embedding_model = embedding_model
        self.cache_dir = Path(cache_dir) if cache_dir else None

        # L1 Cache: Exact match (hash-based)
        self.exact_cache: Dict[str, CachedResponse] = {}

        # L2 Cache: Semantic match (embedding-based)
        self.semantic_cache: List[CachedResponse] = []

        # Statistics
        self.stats = CacheStats()

        # Initialize embedding function
        self._init_embedding_function()

        logger.info(
            f"SemanticCache initialized: threshold={similarity_threshold}, "
            f"max_size={max_cache_size}, ttl={ttl_seconds}s"
        )

    def _init_embedding_function(self):
        """Initialize embedding function based on model type"""
        if self.embedding_model == "simple":
            # Simple TF-IDF-like embedding
            self.embed = self._simple_embedding
        elif self.embedding_model == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embed = self._sentence_transformer_embedding
                logger.info("Using sentence-transformers for embeddings")
            except ImportError:
                logger.warning(
                    "sentence-transformers not available, falling back to simple embedding"
                )
                self.embed = self._simple_embedding
        else:
            self.embed = self._simple_embedding

    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Simple word-based embedding (TF-IDF-like)

        Fast but less accurate than transformer-based embeddings
        """
        # Tokenize and create vocabulary
        words = text.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Create simple embedding vector
        vocab_size = 1000  # Fixed vocabulary size
        embedding = np.zeros(vocab_size)

        for word, count in word_counts.items():
            # Simple hash to vocabulary index
            idx = hash(word) % vocab_size
            embedding[idx] += count

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def _sentence_transformer_embedding(self, text: str) -> np.ndarray:
        """Transformer-based embedding (more accurate)"""
        return self.model.encode(text, convert_to_numpy=True)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get(self, prompt: str, compute_embedding: bool = True) -> Optional[CachedResponse]:
        """
        Get cached response for prompt

        Args:
            prompt: Input prompt
            compute_embedding: Whether to compute embedding for semantic search

        Returns:
            Cached response if found, None otherwise
        """
        self.stats.total_requests += 1

        # L1: Exact match cache
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        if prompt_hash in self.exact_cache:
            cached = self.exact_cache[prompt_hash]

            # Check expiration
            if cached.is_expired(self.ttl_seconds):
                del self.exact_cache[prompt_hash]
                logger.debug(f"Expired exact cache entry: {prompt_hash[:8]}")
            else:
                # Hit!
                cached.update_access()
                self.stats.exact_hits += 1
                self.stats.total_tokens_saved += cached.token_count
                self.stats.total_time_saved_ms += cached.response_time_ms
                logger.debug(f"EXACT CACHE HIT: {prompt[:50]}")
                return cached

        # L2: Semantic similarity cache
        if compute_embedding and self.semantic_cache:
            prompt_embedding = self.embed(prompt)

            best_match = None
            best_similarity = 0.0

            for cached in self.semantic_cache:
                # Skip expired entries
                if cached.is_expired(self.ttl_seconds):
                    continue

                # Calculate similarity
                if cached.embedding is not None:
                    similarity = self._cosine_similarity(prompt_embedding, cached.embedding)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = cached

            # Check if best match exceeds threshold
            if best_match and best_similarity >= self.similarity_threshold:
                best_match.update_access()
                self.stats.semantic_hits += 1
                self.stats.total_tokens_saved += best_match.token_count
                self.stats.total_time_saved_ms += best_match.response_time_ms
                logger.info(
                    f"SEMANTIC CACHE HIT: similarity={best_similarity:.3f}, "
                    f"prompt={prompt[:50]}"
                )
                return best_match

        # Cache miss
        self.stats.misses += 1
        logger.debug(f"Cache miss: {prompt[:50]}")
        return None

    def put(
        self,
        prompt: str,
        response: str,
        token_count: int = 0,
        response_time_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store response in cache

        Args:
            prompt: Input prompt
            response: LLM response
            token_count: Number of tokens in response
            response_time_ms: Response time in milliseconds
            metadata: Additional metadata
        """
        # Create cached entry
        embedding = self.embed(prompt)
        cached = CachedResponse(
            prompt=prompt,
            response=response,
            embedding=embedding,
            token_count=token_count,
            response_time_ms=response_time_ms,
            metadata=metadata or {}
        )

        # L1: Exact cache (hash-based)
        self.exact_cache[cached.prompt_hash] = cached

        # L2: Semantic cache (embedding-based)
        self.semantic_cache.append(cached)

        # Enforce size limits
        self._evict_if_needed()

        logger.debug(f"Cached response: {prompt[:50]}")

    def _evict_if_needed(self):
        """Evict entries if cache exceeds size limit"""
        # Evict from exact cache (LRU)
        if len(self.exact_cache) > self.max_cache_size:
            # Sort by last access time
            sorted_entries = sorted(
                self.exact_cache.items(),
                key=lambda x: x[1].accessed_at
            )
            # Remove oldest
            num_to_remove = len(self.exact_cache) - self.max_cache_size
            for prompt_hash, _ in sorted_entries[:num_to_remove]:
                del self.exact_cache[prompt_hash]

        # Evict from semantic cache
        if len(self.semantic_cache) > self.max_cache_size:
            # Sort by access count and time
            self.semantic_cache.sort(
                key=lambda x: (x.access_count, x.accessed_at),
                reverse=True
            )
            self.semantic_cache = self.semantic_cache[:self.max_cache_size]

    def warm_up(self, prompts: List[Tuple[str, str]]):
        """
        Warm up cache with common prompts

        Args:
            prompts: List of (prompt, response) tuples
        """
        logger.info(f"Warming up cache with {len(prompts)} entries...")
        for prompt, response in prompts:
            self.put(prompt, response)
        logger.info(f"Cache warmed up: {len(self.exact_cache)} entries")

    def clear(self):
        """Clear all cache entries"""
        self.exact_cache.clear()
        self.semantic_cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.stats.to_dict()
        stats.update({
            "exact_cache_size": len(self.exact_cache),
            "semantic_cache_size": len(self.semantic_cache),
            "total_cache_size": len(self.exact_cache) + len(self.semantic_cache)
        })
        return stats

    def save_to_disk(self):
        """Save cache to disk for persistence"""
        if not self.cache_dir:
            logger.warning("No cache directory configured")
            return

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / "semantic_cache.json"

        # Serialize cache (without embeddings - recompute on load)
        cache_data = []
        for cached in self.semantic_cache:
            cache_data.append({
                "prompt": cached.prompt,
                "response": cached.response,
                "token_count": cached.token_count,
                "response_time_ms": cached.response_time_ms,
                "access_count": cached.access_count,
                "metadata": cached.metadata
            })

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

        logger.info(f"Cache saved to {cache_file}")

    def load_from_disk(self):
        """Load cache from disk"""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / "semantic_cache.json"
        if not cache_file.exists():
            logger.info("No cache file found")
            return

        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        # Reload entries (recompute embeddings)
        for entry in cache_data:
            self.put(
                prompt=entry["prompt"],
                response=entry["response"],
                token_count=entry.get("token_count", 0),
                response_time_ms=entry.get("response_time_ms", 0.0),
                metadata=entry.get("metadata", {})
            )

        logger.info(f"Loaded {len(cache_data)} entries from disk")


# ==============================================================================
# TESTING
# ==============================================================================

def test_semantic_cache():
    """Test semantic cache functionality"""
    logging.basicConfig(level=logging.INFO)

    cache = SemanticCache(
        similarity_threshold=0.85,
        max_cache_size=100
    )

    # Test exact match
    prompt1 = "Generate a SQL injection payload for login bypass"
    response1 = "' OR '1'='1' --"
    cache.put(prompt1, response1, token_count=50, response_time_ms=1000)

    result = cache.get(prompt1)
    assert result is not None
    assert result.response == response1
    print("✓ Exact match test passed")

    # Test semantic match
    prompt2 = "Create a SQL injection for authentication bypass"  # Similar
    result = cache.get(prompt2)
    if result:
        print(f"✓ Semantic match found: {result.response}")
    else:
        print("✗ No semantic match (threshold too high)")

    # Test different prompt (no match)
    prompt3 = "What is the weather today?"
    result = cache.get(prompt3)
    assert result is None
    print("✓ No match for unrelated prompt")

    # Stats
    print("\nCache Statistics:")
    print(json.dumps(cache.get_stats(), indent=2))


if __name__ == "__main__":
    test_semantic_cache()
