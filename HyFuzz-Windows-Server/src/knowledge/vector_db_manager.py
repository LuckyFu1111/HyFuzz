"""
Vector Database Manager

This module provides vector database functionality for semantic search and
similarity matching. It supports:
- Multiple similarity metrics (cosine, euclidean, dot product)
- FAISS integration for fast approximate nearest neighbor search
- In-memory and persistent storage
- Batch operations
- Metadata filtering

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import json
import logging
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


# Optional FAISS import for high-performance similarity search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class SimilarityMetric:
    """Supported similarity metrics"""
    COSINE = 'cosine'
    EUCLIDEAN = 'euclidean'
    DOT_PRODUCT = 'dot_product'


@dataclass
class VectorEntry:
    """Single vector database entry"""
    key: str
    vector: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


class VectorDBManager:
    """
    Vector Database Manager

    Manages vector embeddings with support for similarity search,
    metadata filtering, and optional FAISS acceleration.

    Example:
        >>> db = VectorDBManager(dimension=384)
        >>> db.add_embedding("doc1", [0.1, 0.2, ...], {"type": "code"})
        >>> results = db.search_similar([0.1, 0.2, ...], top_k=5)
        >>> print(results[0]['key'], results[0]['similarity'])
    """

    def __init__(
        self,
        dimension: int = 384,
        metric: str = SimilarityMetric.COSINE,
        use_faiss: bool = True,
        normalize_vectors: bool = True
    ):
        """
        Initialize Vector Database

        Args:
            dimension: Dimensionality of vectors
            metric: Similarity metric to use
            use_faiss: Use FAISS if available for faster search
            normalize_vectors: Normalize vectors to unit length
        """
        self.dimension = dimension
        self.metric = metric
        self.normalize_vectors = normalize_vectors
        self.logger = logging.getLogger(__name__)

        # Storage
        self.entries: Dict[str, VectorEntry] = {}
        self.vectors: np.ndarray = np.empty((0, dimension), dtype=np.float32)
        self.keys: List[str] = []

        # FAISS index
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        self.faiss_index = None
        if self.use_faiss:
            self._initialize_faiss_index()

        self.logger.info(
            f"Vector DB initialized: dim={dimension}, metric={metric}, "
            f"faiss={self.use_faiss}, normalize={normalize_vectors}"
        )

    def _initialize_faiss_index(self) -> None:
        """Initialize FAISS index based on metric"""
        try:
            if self.metric == SimilarityMetric.COSINE or self.normalize_vectors:
                # Inner product search on normalized vectors = cosine similarity
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
            elif self.metric == SimilarityMetric.EUCLIDEAN:
                self.faiss_index = faiss.IndexFlatL2(self.dimension)
            else:  # DOT_PRODUCT
                self.faiss_index = faiss.IndexFlatIP(self.dimension)

            self.logger.info(f"FAISS index initialized: {type(self.faiss_index).__name__}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize FAISS: {e}. Using numpy fallback.")
            self.use_faiss = False
            self.faiss_index = None

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length"""
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector

    def add_embedding(
        self,
        key: str,
        vector: List[float] | np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add embedding to database

        Args:
            key: Unique identifier
            vector: Embedding vector
            metadata: Optional metadata dictionary

        Raises:
            ValueError: If vector dimension doesn't match
        """
        # Convert to numpy array
        if isinstance(vector, list):
            vector = np.array(vector, dtype=np.float32)
        elif not isinstance(vector, np.ndarray):
            vector = np.array(vector, dtype=np.float32)

        # Validate dimension
        if vector.shape[0] != self.dimension:
            raise ValueError(
                f"Vector dimension {vector.shape[0]} doesn't match "
                f"database dimension {self.dimension}"
            )

        # Normalize if required
        if self.normalize_vectors:
            vector = self._normalize_vector(vector)

        # Create entry
        import time
        entry = VectorEntry(
            key=key,
            vector=vector,
            metadata=metadata or {},
            timestamp=time.time()
        )

        # Update storage
        if key in self.entries:
            # Update existing
            old_idx = self.keys.index(key)
            self.vectors[old_idx] = vector
            self.entries[key] = entry
        else:
            # Add new
            self.entries[key] = entry
            self.keys.append(key)
            self.vectors = np.vstack([self.vectors, vector.reshape(1, -1)])

            # Update FAISS index
            if self.use_faiss and self.faiss_index is not None:
                self.faiss_index.add(vector.reshape(1, -1))

        self.logger.debug(f"Added embedding: {key}, total={len(self.entries)}")

    def add_embeddings_batch(
        self,
        embeddings: List[Tuple[str, List[float] | np.ndarray, Optional[Dict[str, Any]]]]
    ) -> None:
        """
        Add multiple embeddings efficiently

        Args:
            embeddings: List of (key, vector, metadata) tuples
        """
        for key, vector, metadata in embeddings:
            self.add_embedding(key, vector, metadata)

        self.logger.info(f"Added {len(embeddings)} embeddings in batch")

    def search_similar(
        self,
        query_vector: List[float] | np.ndarray,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            metadata_filter: Filter results by metadata fields
            threshold: Minimum similarity threshold (metric-dependent)

        Returns:
            List of results with keys, similarities, and metadata
        """
        if len(self.entries) == 0:
            return []

        # Convert and normalize query
        if isinstance(query_vector, list):
            query_vector = np.array(query_vector, dtype=np.float32)

        if self.normalize_vectors:
            query_vector = self._normalize_vector(query_vector)

        # Search using FAISS or numpy
        if self.use_faiss and self.faiss_index is not None:
            results = self._search_faiss(query_vector, top_k, metadata_filter, threshold)
        else:
            results = self._search_numpy(query_vector, top_k, metadata_filter, threshold)

        return results

    def _search_faiss(
        self,
        query_vector: np.ndarray,
        top_k: int,
        metadata_filter: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> List[Dict[str, Any]]:
        """Search using FAISS index"""
        # FAISS search
        distances, indices = self.faiss_index.search(
            query_vector.reshape(1, -1),
            min(top_k * 2, len(self.keys))  # Get more for filtering
        )

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.keys):
                continue

            key = self.keys[idx]
            entry = self.entries[key]

            # Convert distance to similarity
            if self.metric == SimilarityMetric.COSINE:
                similarity = float(dist)  # Already cosine similarity (inner product on normalized)
            elif self.metric == SimilarityMetric.EUCLIDEAN:
                similarity = 1.0 / (1.0 + float(dist))  # Convert distance to similarity
            else:  # DOT_PRODUCT
                similarity = float(dist)

            # Apply threshold
            if threshold is not None and similarity < threshold:
                continue

            # Apply metadata filter
            if metadata_filter and not self._matches_filter(entry.metadata, metadata_filter):
                continue

            results.append({
                'key': key,
                'similarity': similarity,
                'metadata': entry.metadata,
                'timestamp': entry.timestamp
            })

            if len(results) >= top_k:
                break

        return results

    def _search_numpy(
        self,
        query_vector: np.ndarray,
        top_k: int,
        metadata_filter: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> List[Dict[str, Any]]:
        """Search using numpy (fallback)"""
        # Compute similarities
        if self.metric == SimilarityMetric.COSINE:
            # Cosine similarity
            similarities = np.dot(self.vectors, query_vector)
        elif self.metric == SimilarityMetric.EUCLIDEAN:
            # Convert euclidean distance to similarity
            distances = np.linalg.norm(self.vectors - query_vector, axis=1)
            similarities = 1.0 / (1.0 + distances)
        else:  # DOT_PRODUCT
            similarities = np.dot(self.vectors, query_vector)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1]

        results = []
        for idx in top_indices:
            key = self.keys[idx]
            entry = self.entries[key]
            similarity = float(similarities[idx])

            # Apply threshold
            if threshold is not None and similarity < threshold:
                continue

            # Apply metadata filter
            if metadata_filter and not self._matches_filter(entry.metadata, metadata_filter):
                continue

            results.append({
                'key': key,
                'similarity': similarity,
                'metadata': entry.metadata,
                'timestamp': entry.timestamp
            })

            if len(results) >= top_k:
                break

        return results

    def _matches_filter(self, metadata: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria"""
        for key, value in filter_dict.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def get_embedding(self, key: str) -> Optional[np.ndarray]:
        """Get embedding by key"""
        entry = self.entries.get(key)
        return entry.vector if entry else None

    def delete_embedding(self, key: str) -> bool:
        """
        Delete embedding by key

        Args:
            key: Key to delete

        Returns:
            True if deleted, False if not found
        """
        if key not in self.entries:
            return False

        # Remove from entries
        del self.entries[key]

        # Remove from keys and vectors
        idx = self.keys.index(key)
        self.keys.pop(idx)
        self.vectors = np.delete(self.vectors, idx, axis=0)

        # Rebuild FAISS index (expensive, but necessary)
        if self.use_faiss:
            self._rebuild_faiss_index()

        self.logger.debug(f"Deleted embedding: {key}")
        return True

    def _rebuild_faiss_index(self) -> None:
        """Rebuild FAISS index from scratch"""
        if not self.use_faiss:
            return

        self._initialize_faiss_index()
        if self.faiss_index is not None and len(self.vectors) > 0:
            self.faiss_index.add(self.vectors)

    def clear(self) -> None:
        """Clear all embeddings"""
        self.entries.clear()
        self.keys.clear()
        self.vectors = np.empty((0, self.dimension), dtype=np.float32)

        if self.use_faiss:
            self._initialize_faiss_index()

        self.logger.info("Vector database cleared")

    def size(self) -> int:
        """Get number of embeddings"""
        return len(self.entries)

    def save(self, filepath: str | Path) -> None:
        """
        Save database to file

        Args:
            filepath: Path to save file (.pkl)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'dimension': self.dimension,
            'metric': self.metric,
            'normalize_vectors': self.normalize_vectors,
            'entries': {
                key: {
                    'vector': entry.vector.tolist(),
                    'metadata': entry.metadata,
                    'timestamp': entry.timestamp
                }
                for key, entry in self.entries.items()
            },
            'keys': self.keys,
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        self.logger.info(f"Saved {len(self.entries)} embeddings to {filepath}")

    @classmethod
    def load(cls, filepath: str | Path, use_faiss: bool = True) -> 'VectorDBManager':
        """
        Load database from file

        Args:
            filepath: Path to load file
            use_faiss: Use FAISS for search

        Returns:
            Loaded VectorDBManager instance
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        # Create new instance
        db = cls(
            dimension=data['dimension'],
            metric=data['metric'],
            use_faiss=use_faiss,
            normalize_vectors=data['normalize_vectors']
        )

        # Restore entries
        for key, entry_data in data['entries'].items():
            db.add_embedding(
                key=key,
                vector=entry_data['vector'],
                metadata=entry_data['metadata']
            )

        db.logger.info(f"Loaded {len(db.entries)} embeddings from {filepath}")
        return db

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_entries': len(self.entries),
            'dimension': self.dimension,
            'metric': self.metric,
            'use_faiss': self.use_faiss,
            'normalize_vectors': self.normalize_vectors,
            'memory_mb': self.vectors.nbytes / (1024 * 1024) if len(self.vectors) > 0 else 0,
        }


def _self_test() -> bool:
    """Basic smoke test for module."""
    try:
        # Test basic operations
        db = VectorDBManager(dimension=128)

        # Add embeddings
        db.add_embedding("doc1", np.random.randn(128).tolist(), {"type": "code", "language": "python"})
        db.add_embedding("doc2", np.random.randn(128).tolist(), {"type": "code", "language": "java"})
        db.add_embedding("doc3", np.random.randn(128).tolist(), {"type": "text"})

        # Search
        query = np.random.randn(128)
        results = db.search_similar(query, top_k=2)
        assert len(results) <= 2

        # Metadata filter
        results = db.search_similar(query, top_k=2, metadata_filter={"type": "code"})
        assert all(r['metadata']['type'] == 'code' for r in results)

        # Stats
        stats = db.get_stats()
        assert stats['total_entries'] == 3

        print(f"Vector DB self-test passed! Stats: {stats}")
        return True

    except Exception as exc:
        print(f"Self test failed: {exc}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    print("="*70)
    print("VECTOR DATABASE MANAGER - SELF TEST")
    print("="*70)
    print(f"FAISS available: {FAISS_AVAILABLE}")
    print()

    success = _self_test()
    print()
    print("="*70)
    print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
    print("="*70)
