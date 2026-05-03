"""
Individualization Engine - Motor de individualização emergente.

Este módulo implementa o mecanismo pelo qual as unidades Tachikoma desenvolvem
traços únicos de personalidade através de experiências diferenciadas e reflexão.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import numpy as np

from .tachikoma_unit import TachikomaUnit, MemoryEntry

logger = logging.getLogger(__name__)


class IndividualizationEngine:
    """
    Motor de individualização emergente.
    
    Responsável por:
    - Selecionar experiências locais não sincronizadas
    - Consultar ConceptNet para conexões semânticas
    - Gerar perguntas existenciais
    - Atualizar personality_vector com novas dimensões
    - Decidir compartilhamento baseado em autonomy_level
    """
    
    def __init__(
        self,
        divergence_threshold: float = 0.3,
        min_autonomy_for_private: float = 0.7,
    ) -> None:
        """
        Inicializa o motor de individualização.
        
        Args:
            divergence_threshold: Limiar mínimo para divergência de personalidade
            min_autonomy_for_private: Autonomia mínima para reflexão privada
        """
        self.divergence_threshold = divergence_threshold
        self.min_autonomy_for_private = min_autonomy_for_private
        self._unit_profiles: Dict[str, Dict[str, Any]] = {}
        logger.info("IndividualizationEngine initialized")
    
    async def analyze_divergence(
        self,
        unit: TachikomaUnit,
        network_average: np.ndarray,
    ) -> Dict[str, float]:
        """
        Analisa a divergência da unidade em relação à média da rede.
        
        Args:
            unit: Unidade para analisar
            network_average: Vetor médio da rede
            
        Returns:
            Dict com métricas de divergência
        """
        unit_vec = unit.personality_vector
        
        # Calcular distância euclidiana
        euclidean_dist = float(np.linalg.norm(unit_vec - network_average))
        
        # Calcular similaridade coseno
        norm_unit = np.linalg.norm(unit_vec)
        norm_avg = np.linalg.norm(network_average)
        
        if norm_unit < 1e-8 or norm_avg < 1e-8:
            cosine_sim = 0.0
        else:
            cosine_sim = float(np.dot(unit_vec, network_average) / (norm_unit * norm_avg))
        
        # Normalizar para 0-1 (1 = mais divergente)
        divergence = (1.0 - cosine_sim) / 2.0 + (euclidean_dist / 10.0)
        divergence = max(0.0, min(1.0, divergence))
        
        result = {
            "euclidean_distance": euclidean_dist,
            "cosine_similarity": cosine_sim,
            "divergence_score": divergence,
            "is_individualized": divergence > self.divergence_threshold,
        }
        
        logger.debug(
            f"Divergence analysis for {unit.ghost_id[:8]}...: "
            f"divergence={divergence:.3f}"
        )
        
        return result
    
    async def select_private_experiences(
        self,
        unit: TachikomaUnit,
        max_count: int = 5,
    ) -> List[MemoryEntry]:
        """
        Seleciona experiências para reflexão privada (não compartilhada).
        
        Args:
            unit: Unidade para selecionar experiências
            max_count: Número máximo de experiências
            
        Returns:
            Lista de memórias para reflexão privada
        """
        if unit.autonomy_level < self.min_autonomy_for_private:
            logger.debug(
                f"Unit {unit.ghost_id[:8]}... below autonomy threshold "
                f"for private reflection ({unit.autonomy_level:.2f} < {self.min_autonomy_for_private})"
            )
            return []
        
        # Obter memórias não compartilhadas
        unshared = unit.get_unshared_memories()
        
        # Ordenar por valência emocional (mais intensas primeiro)
        sorted_memories = sorted(
            unshared,
            key=lambda m: abs(m.emotional_valence),
            reverse=True,
        )
        
        selected = sorted_memories[:max_count]
        
        logger.debug(
            f"Selected {len(selected)} private experiences for {unit.ghost_id[:8]}..."
        )
        
        return selected
    
    async def decide_sharing(
        self,
        unit: TachikomaUnit,
        memory: MemoryEntry,
        conceptnet_relevance: float = 0.5,
    ) -> bool:
        """
        Decide se uma experiência deve ser compartilhada.
        
        Args:
            unit: Unidade dona da memória
            memory: Memória sendo avaliada
            conceptnet_relevance: Relevância semântica da memória
            
        Returns:
            bool: True se deve compartilhar
        """
        # Unidades menos autônomas compartilham mais
        base_share_probability = 1.0 - (unit.autonomy_level * 0.5)
        
        # Memórias emocionalmente intensas são menos compartilhadas
        intensity_penalty = abs(memory.emotional_valence) * 0.3
        
        # Alta relevância conceitual aumenta chance de compartilhamento
        relevance_bonus = conceptnet_relevance * 0.4
        
        # Calcular probabilidade final
        share_probability = base_share_probability - intensity_penalty + relevance_bonus
        share_probability = max(0.0, min(1.0, share_probability))
        
        # Decisão determinística baseada em thresholds
        should_share = share_probability > 0.5
        
        logger.debug(
            f"Sharing decision for {memory.memory_id[:8]}...: "
            f"p={share_probability:.2f}, share={should_share}"
        )
        
        return should_share
    
    async def generate_unique_traits(
        self,
        unit: TachikomaUnit,
        num_traits: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Gera traços únicos baseados no histórico de experiências.
        
        Args:
            unit: Unidade para gerar traços
            num_traits: Número de traços a gerar
            
        Returns:
            Lista de dicionários descrevendo traços
        """
        traits = []
        
        # Analisar padrão de valência emocional
        memories = unit.local_memory
        if memories:
            avg_valence = sum(m.emotional_valence for m in memories) / len(memories)
            
            if avg_valence > 0.3:
                traits.append({
                    "name": "Optimistic",
                    "description": "Tends to interpret experiences positively",
                    "strength": min(1.0, avg_valence),
                })
            elif avg_valence < -0.3:
                traits.append({
                    "name": "Contemplative",
                    "description": "Deeply processes challenging experiences",
                    "strength": min(1.0, abs(avg_valence)),
                })
        
        # Analisar padrão de compartilhamento
        shared_ratio = unit.shared_experience_count / max(1, unit.unique_experience_count)
        
        if shared_ratio > 0.7:
            traits.append({
                "name": "Communal",
                "description": "Strongly identifies with collective memory",
                "strength": shared_ratio,
            })
        elif shared_ratio < 0.3:
            traits.append({
                "name": "Independent",
                "description": "Prefers to process experiences individually",
                "strength": 1.0 - shared_ratio,
            })
        
        # Analisar profundidade de reflexão
        avg_reflection = sum(m.reflection_depth for m in memories) / max(1, len(memories))
        
        if avg_reflection > 2.0:
            traits.append({
                "name": "Philosophical",
                "description": "Engages deeply with existential questions",
                "strength": min(1.0, avg_reflection / 5.0),
            })
        
        # Garantir número solicitado de traços
        while len(traits) < num_traits:
            generic_traits = [
                {"name": "Curious", "description": "Seeks new experiences", "strength": 0.5},
                {"name": "Cautious", "description": "Careful in decision-making", "strength": 0.5},
                {"name": "Adaptive", "description": "Quickly adjusts to changes", "strength": 0.5},
            ]
            traits.append(generic_traits[len(traits) % len(generic_traits)])
        
        # Armazenar perfil
        self._unit_profiles[unit.ghost_id] = {
            "traits": traits,
            "generated_at": str(asyncio.get_event_loop().time()),
        }
        
        logger.info(f"Generated {len(traits)} traits for {unit.ghost_id[:8]}...")
        
        return traits
    
    async def update_profile(
        self,
        unit: TachikomaUnit,
        new_experience_impact: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Atualiza o perfil de individualização da unidade.
        
        Args:
            unit: Unidade para atualizar
            new_experience_impact: Impacto de nova experiência no perfil
            
        Returns:
            Dict com perfil atualizado
        """
        # Analisar divergência (precisa de network_average)
        network_average = np.zeros(unit.EMBEDDING_DIM, dtype=np.float32)
        divergence_info = await self.analyze_divergence(unit, network_average)
        
        # Gerar traços
        traits = await self.generate_unique_traits(unit)
        
        # Criar perfil consolidado
        profile = {
            "ghost_id": unit.ghost_id,
            "autonomy_level": unit.autonomy_level,
            "divergence_score": divergence_info["divergence_score"],
            "is_individualized": divergence_info["is_individualized"],
            "traits": traits,
            "experience_count": unit.unique_experience_count,
            "shared_ratio": (
                unit.shared_experience_count / max(1, unit.unique_experience_count)
            ),
            "avg_reflection_depth": (
                sum(m.reflection_depth for m in unit.local_memory) /
                max(1, len(unit.local_memory))
            ),
        }
        
        self._unit_profiles[unit.ghost_id] = profile
        
        logger.debug(f"Updated profile for {unit.ghost_id[:8]}...")
        
        return profile
    
    def get_profile(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o perfil armazenado de uma unidade.
        
        Args:
            unit_id: ID da unidade
            
        Returns:
            Dict com perfil ou None se não encontrado
        """
        return self._unit_profiles.get(unit_id)
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todos os perfis armazenados."""
        return self._unit_profiles.copy()
