"""
Knowledge Engine Module - Integração com ConceptNet.

Este módulo fornece integração com a base de conhecimento semântico ConceptNet,
permitindo mapeamento de experiências para conceitos, embeddings semânticos,
e raciocínio sobre relações conceituais.
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
