"""
Query Interface Module

Provides high-level query interface for searching and retrieving
memories and concepts from the knowledge base.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import numpy as np
from datetime import datetime

from .conceptnet_loader import ConceptNetLoader
from .graph_embedder import GraphEmbedder
from .semantic_reasoner import SemanticReasoner
from .memory_encoder import MemoryEncoder

logger = logging.getLogger(__name__)


class QueryInterface:
    """
    High-level interface for querying the knowledge base.
    
    Supports semantic search, concept exploration, and
    memory retrieval with various filtering options.
    
    Attributes:
        reasoner: Semantic reasoner instance
        encoder: Memory encoder instance
        memory_store: In-memory store for quick access
    """
    
    def __init__(
        self,
        conceptnet_loader: ConceptNetLoader,
        embedder: GraphEmbedder,
        reasoner: SemanticReasoner,
        encoder: MemoryEncoder
    ):
        """
        Initialize query interface.
        
        Args:
            conceptnet_loader: ConceptNet loader instance
            embedder: Graph embedder instance
            reasoner: Semantic reasoner instance
            encoder: Memory encoder instance
        """
        self.conceptnet_loader = conceptnet_loader
        self.embedder = embedder
        self.reasoner = reasoner
        self.encoder = encoder
        
        # In-memory store for memories
        self.memory_store: Dict[str, Dict[str, Any]] = {}
    
    def add_memory(self, memory_data: Dict[str, Any]) -> str:
        """
        Add a memory to the store.
        
        Args:
            memory_data: Encoded memory dictionary
            
        Returns:
            Memory ID
        """
        memory_id = memory_data.get("memory_id")
        if not memory_id:
            memory_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            memory_data["memory_id"] = memory_id
        
        self.memory_store[memory_id] = memory_data
        logger.debug(f"Added memory {memory_id}")
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory data or None
        """
        return self.memory_store.get(memory_id)
    
    def search_memories(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            filters: Optional filters (shareable, valence range, etc.)
            
        Returns:
            List of matching memories with scores
        """
        # Encode query
        query_embedding = self.embedder.create_embedding(query)
        if query_embedding is None:
            logger.warning("Could not encode query")
            return []
        
        results = []
        
        for memory_id, memory in self.memory_store.items():
            # Apply filters
            if filters:
                if "shareable" in filters:
                    if memory.get("shareable") != filters["shareable"]:
                        continue
                
                if "min_valence" in filters:
                    if memory.get("emotional_valence", 0) < filters["min_valence"]:
                        continue
                
                if "max_valence" in filters:
                    if memory.get("emotional_valence", 0) > filters["max_valence"]:
                        continue
            
            # Compute similarity
            memory_embedding = np.array(memory.get("content_embedding", []))
            if memory_embedding.size == 0:
                continue
            
            similarity = self.embedder.compute_similarity(query_embedding, memory_embedding)
            
            if similarity >= min_similarity:
                results.append({
                    "memory": memory,
                    "score": similarity,
                    "memory_id": memory_id
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def search_by_concept(
        self,
        concept: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories containing a specific concept.
        
        Args:
            concept: Concept URI or label
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        results = []
        
        for memory_id, memory in self.memory_store.items():
            concepts = memory.get("conceptnet_concepts", [])
            
            # Check if concept is in memory
            if concept in concepts or f"/c/en/{concept}" in concepts:
                results.append({
                    "memory": memory,
                    "memory_id": memory_id
                })
            
            if len(results) >= limit:
                break
        
        return results
    
    def find_related_memories(
        self,
        memory_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find memories related to a given memory.
        
        Args:
            memory_id: Source memory ID
            limit: Maximum number of results
            
        Returns:
            List of related memories
        """
        source_memory = self.get_memory(memory_id)
        if not source_memory:
            return []
        
        # Get concepts from source memory
        concepts = source_memory.get("conceptnet_concepts", [])
        
        # Expand concepts using reasoner
        expanded_concepts = self.reasoner.expand_query(concepts, expansion_factor=0.5)
        
        # Search for memories with related concepts
        results = []
        seen_ids = {memory_id}
        
        for concept in expanded_concepts:
            related = self.search_by_concept(concept, limit=limit)
            
            for item in related:
                if item["memory_id"] not in seen_ids:
                    seen_ids.add(item["memory_id"])
                    results.append(item)
                
                if len(results) >= limit:
                    return results
        
        return results
    
    def query_concepts(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Query ConceptNet for relevant concepts.
        
        Args:
            query: Query text
            top_k: Number of concepts to return
            
        Returns:
            List of concept information dictionaries
        """
        # Find similar concepts
        similar = self.conceptnet_loader.find_similar_concepts(query, top_k=top_k)
        
        results = []
        for concept_uri, score in similar:
            context = self.reasoner.get_concept_context(concept_uri, context_size=5)
            results.append({
                "concept": concept_uri,
                "score": score,
                "context": context
            })
        
        return results
    
    def aggregate_memories(
        self,
        memory_ids: List[str],
        aggregation_method: str = "average"
    ) -> Optional[np.ndarray]:
        """
        Aggregate multiple memories into combined representation.
        
        Args:
            memory_ids: List of memory IDs
            aggregation_method: Method ('average', 'weighted')
            
        Returns:
            Combined embedding or None
        """
        memories = []
        for mid in memory_ids:
            memory = self.get_memory(mid)
            if memory:
                memories.append(memory)
        
        if not memories:
            return None
        
        if aggregation_method == "weighted":
            # Weight by reflection depth
            weights = [m.get("reflection_depth", 0.5) + 0.5 for m in memories]
            return self.encoder.merge_memories(memories, weights)
        else:
            return self.encoder.merge_memories(memories)
    
    def get_collective_insights(
        self,
        topic: str,
        min_agreement: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract collective insights about a topic from all memories.
        
        Args:
            topic: Topic of interest
            min_agreement: Minimum agreement threshold
            
        Returns:
            Dictionary with collective insights
        """
        # Search for relevant memories
        relevant = self.search_memories(topic, limit=50, min_similarity=0.3)
        
        if not relevant:
            return {"topic": topic, "insights": [], "consensus": 0.0}
        
        # Analyze valence distribution
        valences = [r["memory"].get("emotional_valence", 0) for r in relevant]
        avg_valence = np.mean(valences)
        valence_std = np.std(valences)
        
        # Determine consensus
        consensus = 1.0 - valence_std  # Lower std = higher consensus
        
        # Extract common concepts
        concept_counts: Dict[str, int] = {}
        for r in relevant:
            for concept in r["memory"].get("conceptnet_concepts", []):
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        # Sort by frequency
        common_concepts = sorted(
            concept_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "topic": topic,
            "num_memories": len(relevant),
            "avg_valence": float(avg_valence),
            "consensus": float(consensus),
            "common_concepts": [{"concept": c, "count": n} for c, n in common_concepts],
            "sample_memories": [r["memory"]["content"] for r in relevant[:5]]
        }
    
    def clear_memories(self) -> None:
        """Clear all memories from store."""
        self.memory_store.clear()
        logger.info("Cleared all memories")
    
    @property
    def memory_count(self) -> int:
        """Get number of stored memories."""
        return len(self.memory_store)
