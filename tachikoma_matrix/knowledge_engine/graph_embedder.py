"""
Graph Embedder - Geração de embeddings para grafos de conhecimento.

Este módulo implementa geração e manipulação de embeddings para o grafo
de conhecimento do ConceptNet usando técnicas como TransE ou node2vec.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class GraphEmbedder:
    """
    Gerador de embeddings para grafos de conhecimento.
    
    Implementa métodos para:
    - Gerar embeddings de nós do grafo
    - Calcular embeddings de arestas (relações)
    - Projetar novos conceitos no espaço de embeddings
    """
    
    def __init__(self, embedding_dim: int = 300) -> None:
        """
        Inicializa o gerador de embeddings.
        
        Args:
            embedding_dim: Dimensão dos vetores de embedding
        """
        self.embedding_dim = embedding_dim
        self.node_embeddings: Dict[str, np.ndarray] = {}
        self.relation_embeddings: Dict[str, np.ndarray] = {}
        logger.info(f"GraphEmbedder initialized (dim={embedding_dim})")
    
    def generate_node_embedding(
        self,
        concept: str,
        seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Gera embedding para um nó do grafo.
        
        Args:
            concept: Nome do conceito
            seed: Seed para reprodutibilidade
            
        Returns:
            Vetor de embedding
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Usar hash do conceito para consistência
        concept_hash = hash(concept)
        np.random.seed(concept_hash)
        
        embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        self.node_embeddings[concept] = embedding
        
        return embedding
    
    def generate_relation_embedding(
        self,
        relation_type: str,
    ) -> np.ndarray:
        """
        Gera embedding para um tipo de relação.
        
        Args:
            relation_type: Tipo de relação (ex: "RelatedTo", "IsA")
            
        Returns:
            Vetor de embedding da relação
        """
        if relation_type in self.relation_embeddings:
            return self.relation_embeddings[relation_type]
        
        # Hash baseado no tipo de relação
        relation_hash = hash(relation_type)
        np.random.seed(relation_hash)
        
        embedding = np.random.randn(self.embedding_dim).astype(np.float32) * 0.5
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        self.relation_embeddings[relation_type] = embedding
        
        return embedding
    
    def project_concept(
        self,
        concept: str,
        related_concepts: List[Tuple[str, str]],
    ) -> np.ndarray:
        """
        Projeta um novo conceito no espaço de embeddings baseado em relações.
        
        Usa uma abordagem tipo TransE: embedding(head) + embedding(relation) ≈ embedding(tail)
        
        Args:
            concept: Novo conceito para projetar
            related_concepts: Lista de tuplas (conceito_relacionado, tipo_relacao)
            
        Returns:
            Vetor de embedding projetado
        """
        if not related_concepts:
            return self.generate_node_embedding(concept)
        
        projections = []
        
        for related_concept, relation_type in related_concepts:
            # Obter embeddings existentes ou gerar novos
            if related_concept in self.node_embeddings:
                related_emb = self.node_embeddings[related_concept]
            else:
                related_emb = self.generate_node_embedding(related_concept)
            
            relation_emb = self.generate_relation_embedding(relation_type)
            
            # Projetar baseado na relação
            if relation_type in ["IsA", "InstanceOf"]:
                # Subclasse tende a estar próxima da superclasse
                projection = related_emb + relation_emb * 0.5
            elif relation_type in ["PartOf", "HasA"]:
                projection = related_emb + relation_emb * 0.3
            else:
                # Relações genéricas
                projection = related_emb + relation_emb * 0.2
            
            projections.append(projection)
        
        # Média das projeções
        if projections:
            final_embedding = np.mean(projections, axis=0)
            final_embedding = final_embedding / (np.linalg.norm(final_embedding) + 1e-8)
        else:
            final_embedding = self.generate_node_embedding(concept)
        
        self.node_embeddings[concept] = final_embedding
        
        return final_embedding
    
    def calculate_relation_score(
        self,
        head: str,
        relation: str,
        tail: str,
    ) -> float:
        """
        Calcula score de plausibilidade para uma tripla (head, relation, tail).
        
        Usa distância L2 no estilo TransE: menor distância = mais plausível
        
        Args:
            head: Conceito cabeça
            relation: Tipo de relação
            tail: Conceito cauda
            
        Returns:
            Score de plausibilidade (0-1, maior = mais plausível)
        """
        # Obter embeddings
        head_emb = self.node_embeddings.get(head)
        tail_emb = self.node_embeddings.get(tail)
        rel_emb = self.relation_embeddings.get(relation)
        
        if head_emb is None:
            head_emb = self.generate_node_embedding(head)
        if tail_emb is None:
            tail_emb = self.generate_node_embedding(tail)
        if rel_emb is None:
            rel_emb = self.generate_relation_embedding(relation)
        
        # Calcular predição TransE: head + relation should be close to tail
        predicted_tail = head_emb + rel_emb
        distance = np.linalg.norm(predicted_tail - tail_emb)
        
        # Converter distância para score 0-1
        score = 1.0 / (1.0 + distance)
        
        return float(score)
    
    def find_analogies(
        self,
        analogy: Tuple[str, str, str],
        limit: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Encontra analogias no formato "a é para b assim como c é para ?".
        
        Exemplo: ("king", "man", "woman") → deveria encontrar "queen"
        
        Args:
            analogy: Tupla (a, b, c) representando "a:b :: c:?"
            limit: Número máximo de resultados
            
        Returns:
            Lista de tuplas (conceito, score)
        """
        a, b, c = analogy
        
        # Obter embeddings
        emb_a = self.node_embeddings.get(a)
        emb_b = self.node_embeddings.get(b)
        emb_c = self.node_embeddings.get(c)
        
        if any(e is None for e in [emb_a, emb_b, emb_c]):
            logger.warning("Missing embeddings for analogy calculation")
            return []
        
        # Calcular vetor de analogia: result = c - a + b
        target_vector = emb_c - emb_a + emb_b
        target_vector = target_vector / (np.linalg.norm(target_vector) + 1e-8)
        
        # Encontrar conceitos mais próximos
        results = []
        
        for concept, embedding in self.node_embeddings.items():
            if concept in [a, b, c]:
                continue
            
            norm_emb = np.linalg.norm(embedding)
            if norm_emb < 1e-8:
                continue
            
            similarity = float(np.dot(target_vector, embedding / norm_emb))
            similarity = (similarity + 1) / 2  # Normalizar para 0-1
            
            results.append((concept, similarity))
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre embeddings gerados."""
        return {
            "node_count": len(self.node_embeddings),
            "relation_count": len(self.relation_embeddings),
            "embedding_dimension": self.embedding_dim,
        }
