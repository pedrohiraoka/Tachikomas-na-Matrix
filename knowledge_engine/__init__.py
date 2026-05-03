"""
Knowledge Engine Module - ConceptNet Integration

This module provides semantic knowledge capabilities using ConceptNet,
enabling Tachikoma units to reason about experiences and form memories.
"""

from .conceptnet_loader import ConceptNetLoader
from .graph_embedder import GraphEmbedder
from .semantic_reasoner import SemanticReasoner
from .memory_encoder import MemoryEncoder
from .query_interface import QueryInterface
from .concept_evolution import ConceptEvolution

__all__ = [
    "ConceptNetLoader",
    "GraphEmbedder",
    "SemanticReasoner",
    "MemoryEncoder",
    "QueryInterface",
    "ConceptEvolution",
]
