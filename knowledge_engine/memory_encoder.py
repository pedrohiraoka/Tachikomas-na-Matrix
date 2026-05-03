"""
Memory Encoder Module

Encodes experiences and memories into semantic representations
using ConceptNet embeddings for storage and retrieval.
"""

import logging
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

from .conceptnet_loader import ConceptNetLoader
from .graph_embedder import GraphEmbedder

logger = logging.getLogger(__name__)


class MemoryEncoder:
    """
    Encodes experiences into semantic memory representations.
    
    Converts raw experience data into embedding vectors and
    extracts relevant ConceptNet concepts for indexing.
    
    Attributes:
        conceptnet_loader: ConceptNet loader instance
        embedder: Graph embedder instance
        emotion_lexicon: Dictionary of emotion-related concepts
    """
    
    def __init__(
        self,
        conceptnet_loader: ConceptNetLoader,
        embedder: GraphEmbedder
    ):
        """
        Initialize memory encoder.
        
        Args:
            conceptnet_loader: ConceptNet loader instance
            embedder: Graph embedder instance
        """
        self.conceptnet_loader = conceptnet_loader
        self.embedder = embedder
        
        # Basic emotion lexicon for valence detection
        self.emotion_lexicon = {
            "positive": ["joy", "happy", "love", "wonder", "curiosity", "discovery"],
            "negative": ["fear", "sadness", "anger", "pain", "confusion", "loss"],
            "neutral": ["observation", "learning", "memory", "thought", "analysis"]
        }
    
    def encode_experience(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Encode an experience into a memory representation.
        
        Args:
            content: Experience content/text
            metadata: Optional additional metadata
            
        Returns:
            Dictionary with encoded memory data
        """
        # Generate embedding
        embedding = self.embedder.create_embedding(content)
        if embedding is None:
            # Fallback to random embedding if no concepts found
            embedding = np.random.randn(300).astype(np.float32)
        
        # Extract concepts from content
        concepts = self.extract_concepts(content)
        
        # Compute emotional valence
        valence = self.compute_valence(content)
        
        # Generate memory ID
        memory_id = self._generate_memory_id(content, datetime.now())
        
        return {
            "memory_id": memory_id,
            "content": content,
            "content_embedding": embedding.tolist(),
            "conceptnet_concepts": concepts,
            "timestamp": datetime.now().isoformat(),
            "emotional_valence": valence,
            "reflection_depth": 0.0,
            "shareable": True,
            "metadata": metadata or {}
        }
    
    def extract_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """
        Extract ConceptNet concepts from text.
        
        Args:
            text: Input text
            max_concepts: Maximum number of concepts to extract
            
        Returns:
            List of concept URIs
        """
        words = text.lower().split()
        concepts = []
        
        # Try single words first
        for word in words:
            # Clean punctuation
            word = word.strip(".,!?;:\"'()[]{}")
            
            # Check if word exists in ConceptNet
            concept_uri = f"/c/en/{word}"
            if concept_uri in self.conceptnet_loader.concepts:
                if concept_uri not in concepts:
                    concepts.append(concept_uri)
            
            if len(concepts) >= max_concepts:
                break
        
        # If not enough concepts, try bigrams
        if len(concepts) < max_concepts:
            for i in range(len(words) - 1):
                bigram = f"{words[i]}_{words[i+1]}".strip(".,!?;:\"'()[]{}")
                concept_uri = f"/c/en/{bigram}"
                
                if concept_uri in self.conceptnet_loader.concepts:
                    if concept_uri not in concepts:
                        concepts.append(concept_uri)
                
                if len(concepts) >= max_concepts:
                    break
        
        return concepts
    
    def compute_valence(self, text: str) -> float:
        """
        Compute emotional valence of text (-1 to 1).
        
        Args:
            text: Input text
            
        Returns:
            Valence score (-1=negative, 0=neutral, 1=positive)
        """
        words = text.lower().split()
        
        positive_count = 0
        negative_count = 0
        
        for word in words:
            word = word.strip(".,!?;:\"'()[]{}")
            
            if word in self.emotion_lexicon["positive"]:
                positive_count += 1
            elif word in self.emotion_lexicon["negative"]:
                negative_count += 1
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        # Normalize to -1 to 1
        valence = (positive_count - negative_count) / total
        return valence
    
    def decode_memory(
        self,
        memory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Decode a memory representation back to readable form.
        
        Args:
            memory_data: Encoded memory dictionary
            
        Returns:
            Decoded memory information
        """
        embedding = np.array(memory_data.get("content_embedding", []))
        
        # Find nearest concepts to the embedding
        nearest_concepts = []
        if embedding.size > 0 and self.embedder.is_trained:
            nearest = self.embedder.find_nearest_entities(embedding, top_k=5)
            nearest_concepts = [c for c, _ in nearest]
        
        return {
            "memory_id": memory_data.get("memory_id"),
            "content": memory_data.get("content", ""),
            "concepts": memory_data.get("conceptnet_concepts", []),
            "nearest_concepts": nearest_concepts,
            "valence": memory_data.get("emotional_valence", 0.0),
            "timestamp": memory_data.get("timestamp"),
            "shareable": memory_data.get("shareable", True),
            "metadata": memory_data.get("metadata", {})
        }
    
    def compare_memories(
        self,
        memory1: Dict[str, Any],
        memory2: Dict[str, Any]
    ) -> float:
        """
        Compute similarity between two memories.
        
        Args:
            memory1: First memory data
            memory2: Second memory data
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = np.array(memory1.get("content_embedding", []))
        emb2 = np.array(memory2.get("content_embedding", []))
        
        if emb1.size == 0 or emb2.size == 0:
            return 0.0
        
        return self.embedder.compute_similarity(emb1, emb2)
    
    def merge_memories(
        self,
        memories: List[Dict[str, Any]],
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Merge multiple memories into a combined embedding.
        
        Args:
            memories: List of memory dictionaries
            weights: Optional weights for each memory
            
        Returns:
            Combined embedding vector
        """
        if not memories:
            return np.zeros(300, dtype=np.float32)
        
        if weights is None:
            weights = [1.0] * len(memories)
        
        embeddings = []
        valid_weights = []
        
        for memory, weight in zip(memories, weights):
            emb = np.array(memory.get("content_embedding", []))
            if emb.size > 0:
                embeddings.append(emb)
                valid_weights.append(weight)
        
        if not embeddings:
            return np.zeros(300, dtype=np.float32)
        
        # Weighted average
        total_weight = sum(valid_weights)
        if total_weight == 0:
            return np.mean(embeddings, axis=0)
        
        combined = sum(emb * w for emb, w in zip(embeddings, valid_weights))
        return combined / total_weight
    
    def _generate_memory_id(self, content: str, timestamp: datetime) -> str:
        """
        Generate unique memory ID.
        
        Args:
            content: Memory content
            timestamp: Creation timestamp
            
        Returns:
            Unique memory ID string
        """
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        time_str = timestamp.strftime("%Y%m%d%H%M%S")
        return f"mem_{time_str}_{content_hash}"
    
    def update_reflection_depth(
        self,
        memory_data: Dict[str, Any],
        depth_increase: float
    ) -> Dict[str, Any]:
        """
        Update the reflection depth of a memory.
        
        Args:
            memory_data: Original memory data
            depth_increase: Amount to increase depth
            
        Returns:
            Updated memory data
        """
        current_depth = memory_data.get("reflection_depth", 0.0)
        new_depth = min(1.0, current_depth + depth_increase)
        
        updated = memory_data.copy()
        updated["reflection_depth"] = new_depth
        
        return updated
