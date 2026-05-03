"""
Graph Embedder Module

Generates and manages graph embeddings for ConceptNet knowledge graph
using Ampligraph or custom embedding techniques.
"""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class GraphEmbedder:
    """
    Generates embeddings for knowledge graph entities and relations.
    
    Supports multiple embedding strategies including pre-trained
    ConceptNet Numberbatch and custom trained embeddings.
    
    Attributes:
        embedding_dim: Dimension of embedding vectors
        embedding_matrix: Matrix of all entity embeddings
        entity_to_idx: Mapping from entity to index
        relation_to_idx: Mapping from relation to index
    """
    
    def __init__(self, embedding_dim: int = 300):
        """
        Initialize graph embedder.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.embedding_matrix: Optional[np.ndarray] = None
        self.entity_to_idx: Dict[str, int] = {}
        self.relation_to_idx: Dict[str, int] = {}
        self._trained = False
        
    def load_from_conceptnet(self, conceptnet_loader) -> bool:
        """
        Load embeddings from ConceptNet loader.
        
        Args:
            conceptnet_loader: ConceptNetLoader instance
            
        Returns:
            True if successful
        """
        if not conceptnet_loader.is_loaded:
            logger.error("ConceptNet not loaded")
            return False
        
        self.embedding_matrix = conceptnet_loader.embeddings.copy()
        self.entity_to_idx = conceptnet_loader.concepts.copy()
        self._trained = True
        
        logger.info(f"Loaded {len(self.entity_to_idx)} entity embeddings")
        return True
    
    def create_embedding(
        self, 
        text: str, 
        method: str = "average"
    ) -> Optional[np.ndarray]:
        """
        Create embedding for text using available concepts.
        
        Args:
            text: Input text to embed
            method: Method for combining word embeddings ('average', 'sum', 'max')
            
        Returns:
            Combined embedding vector or None
        """
        if not self._trained or self.embedding_matrix is None:
            return None
        
        # Tokenize and find matching concepts
        words = text.lower().split()
        embeddings_found = []
        
        for word in words:
            # Try different concept formats
            for fmt in [word, f"/c/en/{word}"]:
                if fmt in self.entity_to_idx:
                    idx = self.entity_to_idx[fmt]
                    embeddings_found.append(self.embedding_matrix[idx])
                    break
        
        if not embeddings_found:
            return None
        
        embeddings_array = np.array(embeddings_found)
        
        if method == "average":
            return np.mean(embeddings_array, axis=0)
        elif method == "sum":
            return np.sum(embeddings_array, axis=0)
        elif method == "max":
            return np.max(embeddings_array, axis=0)
        else:
            return np.mean(embeddings_array, axis=0)
    
    def compute_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
    
    def find_nearest_entities(
        self, 
        embedding: np.ndarray, 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find nearest entities to given embedding.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (entity, similarity) tuples
        """
        if not self._trained or self.embedding_matrix is None:
            return []
        
        # Normalize query embedding
        query_norm = embedding / (np.linalg.norm(embedding) + 1e-10)
        
        # Normalize all embeddings
        matrix_norms = np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True)
        normalized_matrix = self.embedding_matrix / (matrix_norms + 1e-10)
        
        # Compute similarities
        similarities = np.dot(normalized_matrix, query_norm)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        idx_to_entity = {v: k for k, v in self.entity_to_idx.items()}
        results = [
            (idx_to_entity[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
    
    def interpolate_embeddings(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray, 
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Interpolate between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            alpha: Interpolation factor (0=embedding1, 1=embedding2)
            
        Returns:
            Interpolated embedding
        """
        return (1 - alpha) * embedding1 + alpha * embedding2
    
    def save_embeddings(self, path: str) -> bool:
        """
        Save embeddings to file.
        
        Args:
            path: Output file path
            
        Returns:
            True if successful
        """
        try:
            output_path = Path(path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            np.savez_compressed(
                output_path,
                embeddings=self.embedding_matrix,
                entities=list(self.entity_to_idx.keys()),
                indices=list(self.entity_to_idx.values())
            )
            
            logger.info(f"Saved embeddings to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
            return False
    
    def load_embeddings(self, path: str) -> bool:
        """
        Load embeddings from file.
        
        Args:
            path: Input file path
            
        Returns:
            True if successful
        """
        try:
            data = np.load(path, allow_pickle=True)
            
            self.embedding_matrix = data['embeddings']
            entities = list(data['entities'])
            indices = list(data['indices'])
            
            self.entity_to_idx = {e: int(i) for e, i in zip(entities, indices)}
            self._trained = True
            
            logger.info(f"Loaded {len(self.entity_to_idx)} embeddings from {path}")
            return True
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            return False
    
    @property
    def is_trained(self) -> bool:
        """Check if embedder is trained/loaded."""
        return self._trained
    
    @property
    def num_entities(self) -> int:
        """Get number of entities."""
        return len(self.entity_to_idx)
