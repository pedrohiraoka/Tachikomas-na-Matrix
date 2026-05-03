"""
ConceptNet Loader Module

Loads and manages ConceptNet knowledge graph data for semantic reasoning.
Downloads and preprocesses ConceptNet embeddings from the official source.
"""

import gzip
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class ConceptNetLoader:
    """
    Loads and manages ConceptNet knowledge graph data.
    
    Attributes:
        data_dir: Base directory for ConceptNet data files
        embeddings_path: Path to preprocessed embeddings file
        concepts: Dictionary mapping concept URIs to indices
        embeddings: Numpy array of concept embeddings
        relations: Dictionary of relation types
    """
    
    def __init__(self, data_dir: str = "data/conceptnet"):
        """
        Initialize ConceptNet loader.
        
        Args:
            data_dir: Base directory for ConceptNet data
        """
        self.data_dir = Path(data_dir)
        self.embeddings_path = self.data_dir / "numberbatch-19.08.txt"
        self.preprocessed_path = Path("data/embeddings/conceptnet_embeddings.npy")
        self.concepts: Dict[str, int] = {}
        self.embeddings: Optional[np.ndarray] = None
        self.relations: Dict[str, List[Tuple[str, str]]] = {}
        self._loaded = False
        
    async def download_conceptnet(self) -> bool:
        """
        Download ConceptNet embeddings from AWS S3.
        
        Returns:
            True if download successful, False otherwise
        """
        import subprocess
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        gz_path = self.data_dir / "numberbatch-19.08.txt.gz"
        
        if not gz_path.exists():
            logger.info("Downloading ConceptNet embeddings...")
            try:
                cmd = [
                    "wget",
                    "https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-19.08.txt.gz",
                    "-P", str(self.data_dir)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("Download complete, extracting...")
                    with gzip.open(gz_path, 'rb') as f_in:
                        with open(self.embeddings_path, 'wb') as f_out:
                            f_out.write(f_in.read())
                    logger.info(f"Extracted to {self.embeddings_path}")
                    return True
                else:
                    logger.error(f"Download failed: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                logger.error("Download timed out")
                return False
            except Exception as e:
                logger.error(f"Download error: {e}")
                return False
        else:
            logger.info("ConceptNet already downloaded")
            if not self.embeddings_path.exists():
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(self.embeddings_path, 'wb') as f_out:
                        f_out.write(f_in.read())
            return True
    
    async def load_embeddings(self, limit: Optional[int] = None) -> bool:
        """
        Load preprocessed ConceptNet embeddings into memory.
        
        Args:
            limit: Maximum number of embeddings to load (None for all)
            
        Returns:
            True if load successful, False otherwise
        """
        if not self.embeddings_path.exists():
            logger.error("Embeddings file not found. Run download first.")
            return False
            
        logger.info("Loading ConceptNet embeddings...")
        try:
            concepts_list = []
            embeddings_list = []
            
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                        
                    parts = line.strip().split(' ')
                    if len(parts) < 301:  # concept + 300 dimensions
                        continue
                        
                    concept = parts[0]
                    vector = np.array([float(x) for x in parts[1:301]], dtype=np.float32)
                    
                    concepts_list.append(concept)
                    embeddings_list.append(vector)
                    
                    if (i + 1) % 10000 == 0:
                        logger.info(f"Loaded {i + 1} concepts...")
            
            self.concepts = {c: i for i, c in enumerate(concepts_list)}
            self.embeddings = np.array(embeddings_list, dtype=np.float32)
            self._loaded = True
            
            logger.info(f"Loaded {len(self.concepts)} concepts with {self.embeddings.shape[1]} dimensions")
            return True
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            return False
    
    def get_embedding(self, concept: str) -> Optional[np.ndarray]:
        """
        Get embedding for a specific concept.
        
        Args:
            concept: Concept URI or label
            
        Returns:
            Embedding vector or None if not found
        """
        if not self._loaded:
            return None
            
        # Try direct lookup
        if concept in self.concepts:
            return self.embeddings[self.concepts[concept]]
        
        # Try with standard prefix
        normalized = f"/c/en/{concept.lower()}" if not concept.startswith('/') else concept
        if normalized in self.concepts:
            return self.embeddings[self.concepts[normalized]]
        
        return None
    
    def find_similar_concepts(
        self, 
        concept: str, 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find concepts similar to the given concept.
        
        Args:
            concept: Source concept
            top_k: Number of similar concepts to return
            
        Returns:
            List of (concept, similarity_score) tuples
        """
        if not self._loaded or self.embeddings is None:
            return []
            
        query_embedding = self.get_embedding(concept)
        if query_embedding is None:
            return []
        
        # Compute cosine similarities
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        normalized_embeddings = self.embeddings / (norms + 1e-10)
        normalized_query = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        
        similarities = np.dot(normalized_embeddings, normalized_query).flatten()
        
        # Get top-k indices (excluding self)
        query_idx = self.concepts.get(concept, -1)
        top_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in top_indices:
            if idx == query_idx:
                continue
            if len(results) >= top_k:
                break
            concept_name = list(self.concepts.keys())[idx]
            results.append((concept_name, float(similarities[idx])))
        
        return results
    
    def add_relation(self, relation_type: str, concept1: str, concept2: str) -> None:
        """
        Add a relation between two concepts.
        
        Args:
            relation_type: Type of relation (e.g., 'RelatedTo', 'IsA')
            concept1: First concept URI
            concept2: Second concept URI
        """
        if relation_type not in self.relations:
            self.relations[relation_type] = []
        self.relations[relation_type].append((concept1, concept2))
    
    def get_relations(self, concept: str, relation_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get all relations for a concept.
        
        Args:
            concept: Concept URI
            relation_type: Optional filter by relation type
            
        Returns:
            Dictionary mapping relation types to lists of related concepts
        """
        results: Dict[str, List[str]] = {}
        
        for rel_type, pairs in self.relations.items():
            if relation_type and rel_type != relation_type:
                continue
                
            related = []
            for c1, c2 in pairs:
                if c1 == concept:
                    related.append(c2)
                elif c2 == concept:
                    related.append(c1)
            
            if related:
                results[rel_type] = related
        
        return results
    
    @property
    def is_loaded(self) -> bool:
        """Check if embeddings are loaded."""
        return self._loaded
    
    @property
    def vocabulary_size(self) -> int:
        """Get number of loaded concepts."""
        return len(self.concepts)
    
    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension size."""
        if self.embeddings is not None:
            return self.embeddings.shape[1]
        return 300
