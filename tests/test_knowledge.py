"""Test knowledge engine modules."""
import pytest
import numpy as np
from knowledge_engine.graph_embedder import GraphEmbedder


def test_graph_embedder_init():
    """Test GraphEmbedder initialization."""
    embedder = GraphEmbedder(embedding_dim=300)
    assert embedder.embedding_dim == 300
    assert not embedder.is_trained


def test_similarity_calculation():
    """Test embedding similarity."""
    embedder = GraphEmbedder()
    embedder.embedding_matrix = np.random.randn(10, 300).astype(np.float32)
    embedder.entity_to_idx = {f"entity_{i}": i for i in range(10)}
    embedder._trained = True
    
    emb1 = np.random.randn(300).astype(np.float32)
    emb2 = emb1.copy()
    
    sim = embedder.compute_similarity(emb1, emb2)
    assert abs(sim - 1.0) < 0.001  # Should be ~1.0 for identical vectors
