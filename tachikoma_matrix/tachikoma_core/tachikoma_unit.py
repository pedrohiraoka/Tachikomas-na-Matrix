"""
TachikomaUnit - Classe base para unidades Tachikoma.

Cada Tachikoma possui:
- ghost_id (uuid): Identificador único da unidade
- local_memory (List[np.ndarray]): Vetor de embeddings das memórias locais
- shared_memory_pool (Reference): Referência à memória coletiva da rede
- personality_vector (np.ndarray): Embedding evolutivo da personalidade (300 dimensões)
- autonomy_level (float): Nível de autonomia (0.0 a 1.0)
- trust_score (float): Score de confiança para sincronização
- hardware_signature (str): Assinatura única do hardware simulado

Exemplo de uso:
    >>> unit = TachikomaUnit(ghost_id="unit-001")
    >>> await unit.store_experience("Vi algo interessante hoje", shareable=True)
    >>> state = unit.get_state()
    >>> print(state['autonomy_level'])
"""

import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Representa uma entrada de memória individual."""
    
    memory_id: str
    content: str
    embedding: np.ndarray
    conceptnet_concepts: List[str]
    timestamp: datetime
    shareable: bool
    reflection_depth: float = 0.0
    emotional_valence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a memória para dicionário serializável."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "embedding": self.embedding.tolist(),
            "conceptnet_concepts": self.conceptnet_concepts,
            "timestamp": self.timestamp.isoformat(),
            "shareable": self.shareable,
            "reflection_depth": self.reflection_depth,
            "emotional_valence": self.emotional_valence,
            "metadata": self.metadata,
        }


class TachikomaUnit:
    """
    Unidade Tachikoma - Agente de IA com capacidade de aprendizado e reflexão.
    
    Atributos:
        ghost_id: Identificador único UUID da unidade
        hardware_signature: Assinatura do hardware simulado
        personality_vector: Vetor de personalidade (300 dimensões)
        autonomy_level: Nível de autonomia atual (0.0-1.0)
        trust_score: Score de confiança para sincronização
        local_memory: Lista de memórias locais
        shared_memory_pool: Referência ao pool de memória compartilhada
        last_sync_timestamp: Timestamp da última sincronização
        unique_experience_count: Contador de experiências únicas
        shared_experience_count: Contador de experiências compartilhadas
    """
    
    EMBEDDING_DIM = 300
    
    def __init__(
        self,
        ghost_id: Optional[str] = None,
        hardware_signature: Optional[str] = None,
        initial_autonomy: float = 0.5,
    ) -> None:
        """
        Inicializa uma nova unidade Tachikoma.
        
        Args:
            ghost_id: ID único da unidade (gerado se None)
            hardware_signature: Assinatura do hardware (gerada se None)
            initial_autonomy: Nível inicial de autonomia (default: 0.5)
        """
        self.ghost_id = ghost_id or str(uuid.uuid4())
        self.hardware_signature = hardware_signature or self._generate_hardware_signature()
        self.personality_vector: np.ndarray = np.random.randn(self.EMBEDDING_DIM).astype(np.float32) * 0.1
        self.autonomy_level: float = max(0.0, min(1.0, initial_autonomy))
        self.trust_score: float = 1.0
        self.local_memory: List[MemoryEntry] = []
        self.shared_memory_pool: Optional[Any] = None
        self.last_sync_timestamp: Optional[datetime] = None
        self.unique_experience_count: int = 0
        self.shared_experience_count: int = 0
        self._lock = asyncio.Lock()
        
        logger.info(f"TachikomaUnit initialized: {self.ghost_id[:8]}...")
    
    def _generate_hardware_signature(self) -> str:
        """Gera uma assinatura única de hardware simulado."""
        return f"HW-{uuid.uuid4().hex[:12].upper()}"
    
    async def store_experience(
        self,
        content: str,
        embedding: Optional[np.ndarray] = None,
        shareable: bool = True,
        emotional_valence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """
        Armazena uma nova experiência na memória local.
        
        Args:
            content: Conteúdo textual da experiência
            embedding: Vetor de embedding (gerado se None)
            shareable: Se a experiência pode ser compartilhada
            emotional_valence: Valência emocional (-1.0 a 1.0)
            metadata: Metadados adicionais
            
        Returns:
            MemoryEntry: A entrada de memória criada
        """
        async with self._lock:
            if embedding is None:
                embedding = np.random.randn(self.EMBEDDING_DIM).astype(np.float32) * 0.5
            
            memory_entry = MemoryEntry(
                memory_id=str(uuid.uuid4()),
                content=content,
                embedding=embedding,
                conceptnet_concepts=[],
                timestamp=datetime.utcnow(),
                shareable=shareable,
                emotional_valence=max(-1.0, min(1.0, emotional_valence)),
                metadata=metadata or {},
            )
            
            self.local_memory.append(memory_entry)
            self.unique_experience_count += 1
            
            if shareable:
                self.shared_experience_count += 1
            
            logger.debug(
                f"Stored experience for {self.ghost_id[:8]}...: {content[:50]}..."
            )
            
            return memory_entry
    
    async def update_personality_vector(
        self,
        delta: np.ndarray,
        learning_rate: float = 0.01,
    ) -> None:
        """
        Atualiza o vetor de personalidade com base em novas experiências.
        
        Args:
            delta: Vetor de mudança a ser aplicado
            learning_rate: Taxa de aprendizado (default: 0.01)
        """
        async with self._lock:
            delta_norm = delta / (np.linalg.norm(delta) + 1e-8)
            self.personality_vector += delta_norm * learning_rate
            self.personality_vector = self.personality_vector.astype(np.float32)
            
            logger.debug(
                f"Personality vector updated for {self.ghost_id[:8]}... "
                f"(norm: {np.linalg.norm(self.personality_vector):.4f})"
            )
    
    async def adjust_autonomy(self, delta: float) -> float:
        """
        Ajusta o nível de autonomia da unidade.
        
        Args:
            delta: Mudança no nível de autonomia
            
        Returns:
            float: Novo nível de autonomia
        """
        async with self._lock:
            old_autonomy = self.autonomy_level
            self.autonomy_level = max(0.0, min(1.0, self.autonomy_level + delta))
            
            logger.info(
                f"Autonomy adjusted for {self.ghost_id[:8]}...: "
                f"{old_autonomy:.3f} -> {self.autonomy_level:.3f} ({delta:+.3f})"
            )
            
            return self.autonomy_level
    
    def get_state(self) -> Dict[str, Any]:
        """
        Retorna o estado atual da unidade.
        
        Returns:
            Dict contendo todos os atributos relevantes da unidade
        """
        return {
            "ghost_id": self.ghost_id,
            "hardware_signature": self.hardware_signature,
            "personality_vector": self.personality_vector.tolist(),
            "autonomy_level": self.autonomy_level,
            "trust_score": self.trust_score,
            "last_sync_timestamp": (
                self.last_sync_timestamp.isoformat() 
                if self.last_sync_timestamp else None
            ),
            "unique_experience_count": self.unique_experience_count,
            "shared_experience_count": self.shared_experience_count,
            "local_memory_count": len(self.local_memory),
        }
    
    def get_recent_memories(self, limit: int = 10) -> List[MemoryEntry]:
        """
        Retorna as memórias mais recentes.
        
        Args:
            limit: Número máximo de memórias a retornar
            
        Returns:
            Lista de MemoryEntry ordenadas por timestamp (mais recentes primeiro)
        """
        sorted_memories = sorted(
            self.local_memory, 
            key=lambda m: m.timestamp, 
            reverse=True
        )
        return sorted_memories[:limit]
    
    def get_unshared_memories(self) -> List[MemoryEntry]:
        """Retorna memórias marcadas como compartilháveis mas não sincronizadas."""
        return [m for m in self.local_memory if m.shareable and m.reflection_depth == 0]
    
    async def sync_with_pool(self, pool: Any) -> None:
        """
        Sincroniza memórias locais com o pool compartilhado.
        
        Args:
            pool: Referência ao SharedMemoryPool
        """
        self.shared_memory_pool = pool
        self.last_sync_timestamp = datetime.utcnow()
        logger.info(f"Synced with pool for {self.ghost_id[:8]}...")
    
    def calculate_similarity(self, other: 'TachikomaUnit') -> float:
        """
        Calcula similaridade de personalidade com outra unidade.
        
        Args:
            other: Outra unidade Tachikoma
            
        Returns:
            float: Similaridade coseno entre os vetores de personalidade (0-1)
        """
        norm_self = np.linalg.norm(self.personality_vector)
        norm_other = np.linalg.norm(other.personality_vector)
        
        if norm_self < 1e-8 or norm_other < 1e-8:
            return 0.0
        
        cosine_sim = np.dot(self.personality_vector, other.personality_vector) / (
            norm_self * norm_other
        )
        return float((cosine_sim + 1) / 2)
    
    def __repr__(self) -> str:
        return (
            f"TachikomaUnit(ghost_id='{self.ghost_id[:8]}...', "
            f"autonomy={self.autonomy_level:.3f}, "
            f"memories={len(self.local_memory)})"
        )
