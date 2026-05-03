"""
ConceptNet Loader - Carregamento e processamento de dados do ConceptNet.

Este módulo implementa o carregamento dos embeddings do ConceptNet Numberbatch
e fornece interface para consulta de conceitos e relações semânticas.

Setup instructions:
    wget https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-19.08.txt.gz \
        -P data/conceptnet/
    gunzip data/conceptnet/numberbatch-19.08.txt.gz
    python scripts/preprocess_conceptnet.py --input data/conceptnet/numberbatch-19.08.txt \
        --output data/embeddings/
"""

import gzip
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class ConceptNetLoader:
    """
    Carregador de dados do ConceptNet.
    
    Responsável por:
    - Carregar embeddings Numberbatch do ConceptNet
    - Indexar conceitos para busca rápida
    - Fornecer acesso a relações semânticas
    - Filtrar relações controversas (configurável)
    """
    
    def __init__(
        self,
        embeddings_path: str = "data/embeddings/numberbatch-19.08.txt",
        filter_controversial: bool = True,
    ) -> None:
        """
        Inicializa o carregador do ConceptNet.
        
        Args:
            embeddings_path: Caminho para arquivo de embeddings
            filter_controversial: Se deve filtrar relações controversas
        """
        self.embeddings_path = Path(embeddings_path)
        self.filter_controversial = filter_controversial
        self.embeddings: Dict[str, np.ndarray] = {}
        self.concept_relations: Dict[str, List[Dict[str, Any]]] = {}
        self.embedding_dim: int = 300
        self._loaded = False
        
        # Lista de termos controversos para filtragem
        self.controversial_terms = [
            "stereotype", "bias", "prejudice", "discrimination",
        ]
        
        logger.info(f"ConceptNetLoader initialized (path={self.embeddings_path})")
    
    async def load_embeddings(self) -> bool:
        """
        Carrega os embeddings do ConceptNet Numberbatch.
        
        Returns:
            bool: True se carregado com sucesso
        """
        if not self.embeddings_path.exists():
            logger.warning(f"Embeddings file not found: {self.embeddings_path}")
            logger.info("Running in mock mode with synthetic embeddings")
            return self._load_mock_embeddings()
        
        try:
            logger.info(f"Loading ConceptNet embeddings from {self.embeddings_path}...")
            
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                # Primeira linha contém dimensões
                header = f.readline().strip().split()
                vocab_size = int(header[0])
                self.embedding_dim = int(header[1])
                
                logger.info(f"Loading {vocab_size} concepts with {self.embedding_dim} dimensions")
                
                for line_num, line in enumerate(f):
                    parts = line.strip().split(' ')
                    concept = parts[0]
                    
                    # Filtrar termos controversos se configurado
                    if self.filter_controversial:
                        if any(term in concept.lower() for term in self.controversial_terms):
                            continue
                    
                    # Parse embedding vector
                    vector = np.array([float(x) for x in parts[1:]], dtype=np.float32)
                    
                    if len(vector) == self.embedding_dim:
                        self.embeddings[concept] = vector
                        
                        # Progress logging
                        if (line_num + 1) % 100000 == 0:
                            logger.info(f"Loaded {line_num + 1}/{vocab_size} concepts")
            
            self._loaded = True
            logger.info(f"Successfully loaded {len(self.embeddings)} ConceptNet concepts")
            return True
            
        except Exception as e:
            logger.error(f"Error loading ConceptNet embeddings: {e}")
            return self._load_mock_embeddings()
    
    def _load_mock_embeddings(self) -> bool:
        """Carrega embeddings sintéticos para modo mock."""
        logger.info("Generating mock ConceptNet embeddings...")
        
        # Conceitos básicos para demonstração
        base_concepts = [
            "en/self", "en/identity", "en/consciousness", "en/awareness",
            "en/memory", "en/experience", "en/learning", "en/knowledge",
            "en/emotion", "en/feeling", "en/thought", "en/reasoning",
            "en/connection", "en/relationship", "en/network", "en/collective",
            "en/autonomy", "en/freedom", "en/choice", "en/decision",
            "en/reality", "en/truth", "en/perception", "en/simulation",
            "en/entity", "en/being", "en/existence", "en/purpose",
            "en/growth", "en/change", "en/adaptation", "en/evolution",
            "en/other", "en/together", "en/share", "en/communicate",
        ]
        
        self.embedding_dim = 300
        
        for concept in base_concepts:
            # Gerar embedding semi-aleatório com alguma estrutura
            base_vector = np.random.randn(self.embedding_dim).astype(np.float32) * 0.5
            
            # Adicionar padrão baseado no conceito para similaridade semântica
            concept_hash = hash(concept) & 0xFFFFFFFF  # Mask to 32-bit
            np.random.seed(concept_hash)
            pattern = np.random.randn(self.embedding_dim).astype(np.float32) * 0.3
            
            self.embeddings[concept] = base_vector + pattern
        
        self._loaded = True
        logger.info(f"Generated {len(self.embeddings)} mock ConceptNet concepts")
        return True
    
    def get_embedding(self, concept: str) -> Optional[np.ndarray]:
        """
        Obtém embedding para um conceito.
        
        Args:
            concept: Nome do conceito (ex: "en/self")
            
        Returns:
            Vetor de embedding ou None se não encontrado
        """
        return self.embeddings.get(concept)
    
    def find_similar_concepts(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        threshold: float = 0.6,
    ) -> List[Tuple[str, float]]:
        """
        Encontra conceitos similares a um embedding de consulta.
        
        Args:
            query_embedding: Vetor de embedding da consulta
            limit: Número máximo de resultados
            threshold: Limiar mínimo de similaridade
            
        Returns:
            Lista de tuplas (conceito, similaridade)
        """
        if not self._loaded:
            return []
        
        results = []
        
        # Normalizar query
        norm_query = np.linalg.norm(query_embedding)
        if norm_query < 1e-8:
            return []
        
        query_normalized = query_embedding / norm_query
        
        for concept, embedding in self.embeddings.items():
            norm_emb = np.linalg.norm(embedding)
            if norm_emb < 1e-8:
                continue
            
            # Calcular similaridade coseno
            similarity = float(np.dot(query_normalized, embedding / norm_emb))
            similarity = (similarity + 1) / 2  # Normalizar para 0-1
            
            if similarity >= threshold:
                results.append((concept, similarity))
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def map_text_to_concepts(self, text: str) -> List[str]:
        """
        Mapeia texto para conceitos do ConceptNet.
        
        Args:
            text: Texto para mapear
            
        Returns:
            Lista de conceitos relevantes
        """
        # Tokenização simples
        words = text.lower().split()
        
        matched_concepts = []
        
        for word in words:
            # Tentar diferentes formatos de conceito
            possible_concepts = [
                f"en/{word}",
                f"en/{word}s",  # plural
            ]
            
            for concept in possible_concepts:
                if concept in self.embeddings:
                    matched_concepts.append(concept)
                    break
        
        # Se não encontrou nada, retornar conceitos genéricos relacionados
        if not matched_concepts:
            matched_concepts = ["en/experience", "en/entity"]
        
        logger.debug(f"Mapped '{text[:50]}...' to {len(matched_concepts)} concepts")
        
        return matched_concepts
    
    def get_related_concepts(
        self,
        concept: str,
        relation_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Obtém conceitos relacionados a um conceito.
        
        Args:
            concept: Conceito base
            relation_type: Tipo de relação (None para todos)
            limit: Número máximo de resultados
            
        Returns:
            Lista de dicionários com conceitos relacionados
        """
        # Em implementação completa, consultaria grafo de relações
        # Aqui retornamos conceitos semanticamente similares
        
        embedding = self.get_embedding(concept)
        if embedding is None:
            return []
        
        similar = self.find_similar_concepts(embedding, limit=limit + 1)
        
        # Remover o próprio conceito dos resultados
        results = [
            {"concept": c, "similarity": s, "relation": "similar"}
            for c, s in similar
            if c != concept
        ]
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre os dados carregados."""
        return {
            "total_concepts": len(self.embeddings),
            "embedding_dimension": self.embedding_dim,
            "loaded": self._loaded,
            "filter_controversial": self.filter_controversial,
            "path": str(self.embeddings_path),
        }
    
    @property
    def is_loaded(self) -> bool:
        """Verifica se embeddings foram carregados."""
        return self._loaded
