"""
Semantic Reasoner Module

Provides semantic reasoning capabilities using ConceptNet knowledge graph.
Enables Tachikoma units to make inferences and connections between concepts.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from .conceptnet_loader import ConceptNetLoader
from .graph_embedder import GraphEmbedder

logger = logging.getLogger(__name__)


class SemanticReasoner:
    """
    Performs semantic reasoning over ConceptNet knowledge graph.
    
    Supports various reasoning tasks including:
    - Concept association and relatedness
    - Analogical reasoning
    - Inference chains
    - Semantic similarity
    
    Attributes:
        conceptnet_loader: ConceptNet loader instance
        embedder: Graph embedder instance
        inference_depth: Maximum depth for inference chains
    """
    
    def __init__(
        self,
        conceptnet_loader: ConceptNetLoader,
        embedder: GraphEmbedder,
        inference_depth: int = 3
    ):
        """
        Initialize semantic reasoner.
        
        Args:
            conceptnet_loader: ConceptNet loader instance
            embedder: Graph embedder instance
            inference_depth: Maximum inference chain depth
        """
        self.conceptnet_loader = conceptnet_loader
        self.embedder = embedder
        self.inference_depth = inference_depth
        
    def find_associations(
        self,
        concept: str,
        relation_types: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Find concepts associated with the given concept.
        
        Args:
            concept: Source concept
            relation_types: Optional filter by relation types
            max_results: Maximum number of results
            
        Returns:
            List of association dictionaries
        """
        relations = self.conceptnet_loader.get_relations(concept)
        
        if not relations:
            # Try to find via embedding similarity
            embedding = self.conceptnet_loader.get_embedding(concept)
            if embedding is not None:
                similar = self.conceptnet_loader.find_similar_concepts(concept, top_k=max_results)
                return [
                    {"concept": c, "relation": "SimilarTo", "score": s}
                    for c, s in similar
                ]
            return []
        
        results = []
        for rel_type, related_concepts in relations.items():
            if relation_types and rel_type not in relation_types:
                continue
                
            for related in related_concepts[:max_results // len(relations) + 1]:
                results.append({
                    "concept": related,
                    "relation": rel_type,
                    "source": concept
                })
        
        return results[:max_results]
    
    def compute_relatedness(self, concept1: str, concept2: str) -> float:
        """
        Compute semantic relatedness between two concepts.
        
        Uses a combination of:
        - Path-based measures in the graph
        - Embedding similarity
        
        Args:
            concept1: First concept
            concept2: Second concept
            
        Returns:
            Relatedness score (0-1)
        """
        # Check direct relations first
        rels1 = self.conceptnet_loader.get_relations(concept1)
        for rel_type, related in rels1.items():
            if concept2 in related:
                return 1.0
        
        # Use embedding similarity
        emb1 = self.conceptnet_loader.get_embedding(concept1)
        emb2 = self.conceptnet_loader.get_embedding(concept2)
        
        if emb1 is not None and emb2 is not None:
            similarity = self.embedder.compute_similarity(emb1, emb2)
            return max(0.0, min(1.0, (similarity + 1) / 2))  # Normalize to 0-1
        
        return 0.0
    
    def infer_chain(
        self,
        start_concept: str,
        end_concept: str,
        max_length: int = 5
    ) -> Optional[List[Dict]]:
        """
        Find an inference chain between two concepts.
        
        Args:
            start_concept: Starting concept
            end_concept: Target concept
            max_length: Maximum chain length
            
        Returns:
            List of steps in the chain, or None if no path found
        """
        from collections import deque
        
        visited: Set[str] = {start_concept}
        queue = deque([(start_concept, [])])
        
        while queue:
            current, path = queue.popleft()
            
            if len(path) >= max_length:
                continue
            
            relations = self.conceptnet_loader.get_relations(current)
            
            for rel_type, related_list in relations.items():
                for related in related_list:
                    if related == end_concept:
                        return path + [{
                            "from": current,
                            "to": related,
                            "relation": rel_type
                        }]
                    
                    if related not in visited:
                        visited.add(related)
                        new_path = path + [{
                            "from": current,
                            "to": related,
                            "relation": rel_type
                        }]
                        queue.append((related, new_path))
        
        return None
    
    def analogical_reasoning(
        self,
        a: str,
        b: str,
        c: str
    ) -> Optional[str]:
        """
        Perform analogical reasoning: a is to b as c is to ?
        
        Uses embedding arithmetic: result = b - a + c
        
        Args:
            a: First term of source analogy
            b: Second term of source analogy
            c: First term of target analogy
            
        Returns:
            Most likely fourth term, or None
        """
        emb_a = self.conceptnet_loader.get_embedding(a)
        emb_b = self.conceptnet_loader.get_embedding(b)
        emb_c = self.conceptnet_loader.get_embedding(c)
        
        if any(e is None for e in [emb_a, emb_b, emb_c]):
            return None
        
        # Compute analogy vector
        result_vector = emb_b - emb_a + emb_c
        
        # Find nearest concept
        nearest = self.embedder.find_nearest_entities(result_vector, top_k=5)
        
        # Filter out input concepts
        for concept, score in nearest:
            if concept not in [a, b, c]:
                return concept
        
        return None
    
    def expand_query(
        self,
        query_concepts: List[str],
        expansion_factor: float = 0.3
    ) -> List[str]:
        """
        Expand a query with related concepts.
        
        Args:
            query_concepts: Original query concepts
            expansion_factor: Fraction of additional concepts to add
            
        Returns:
            Expanded list of concepts
        """
        expanded = set(query_concepts)
        
        num_to_add = int(len(query_concepts) * expansion_factor)
        
        for concept in query_concepts:
            if len(expanded) >= len(query_concepts) + num_to_add:
                break
                
            associations = self.find_associations(concept, max_results=5)
            for assoc in associations:
                if len(expanded) >= len(query_concepts) + num_to_add:
                    break
                expanded.add(assoc["concept"])
        
        return list(expanded)
    
    def detect_contradictions(
        self,
        statements: List[Dict]
    ) -> List[Tuple[Dict, Dict, str]]:
        """
        Detect potential contradictions in a set of statements.
        
        Args:
            statements: List of statement dictionaries with 'subject', 'predicate', 'object'
            
        Returns:
            List of contradictory statement pairs with reason
        """
        contradictions = []
        
        # Simple contradiction detection based on antonym relations
        antonym_pairs = set()
        for stmt in statements:
            obj = stmt.get("object", "")
            antonyms = self.conceptnet_loader.get_relations(obj, "Antonym")
            if "Antonym" in antonyms:
                for antonym in antonyms["Antonym"]:
                    antonym_pairs.add((obj, antonym))
        
        # Check for contradictions
        for i, stmt1 in enumerate(statements):
            for stmt2 in statements[i+1:]:
                if stmt1.get("subject") == stmt2.get("subject"):
                    obj1 = stmt1.get("object", "")
                    obj2 = stmt2.get("object", "")
                    
                    if (obj1, obj2) in antonym_pairs or (obj2, obj1) in antonym_pairs:
                        contradictions.append((stmt1, stmt2, "Antonym conflict"))
        
        return contradictions
    
    def get_concept_context(
        self,
        concept: str,
        context_size: int = 10
    ) -> Dict:
        """
        Get contextual information about a concept.
        
        Args:
            concept: Target concept
            context_size: Number of related concepts to include
            
        Returns:
            Dictionary with concept context information
        """
        associations = self.find_associations(concept, max_results=context_size)
        
        # Categorize by relation type
        categorized: Dict[str, List[str]] = {}
        for assoc in associations:
            rel = assoc["relation"]
            if rel not in categorized:
                categorized[rel] = []
            categorized[rel].append(assoc["concept"])
        
        # Get embedding statistics
        embedding = self.conceptnet_loader.get_embedding(concept)
        embedding_stats = {}
        if embedding is not None:
            embedding_stats = {
                "mean": float(np.mean(embedding)),
                "std": float(np.std(embedding)),
                "norm": float(np.linalg.norm(embedding))
            }
        
        return {
            "concept": concept,
            "associations": categorized,
            "embedding_stats": embedding_stats,
            "num_relations": sum(len(v) for v in categorized.values())
        }
