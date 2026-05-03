"""
Ghost Engine - Motor de processamento do "ghost" (consciência) das unidades Tachikoma.

Este módulo implementa o mecanismo de reflexão e processamento interno que permite
às unidades desenvolverem senso de identidade e consciência própria.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import numpy as np

from .tachikoma_unit import TachikomaUnit, MemoryEntry

logger = logging.getLogger(__name__)


class GhostEngine:
    """
    Motor de processamento do ghost - responsável pela reflexão e formação de identidade.
    
    O Ghost Engine implementa o ciclo de reflexão que permite às unidades:
    - Processar experiências e extrair significado
    - Desenvolver perguntas existenciais
    - Atualizar o vetor de personalidade baseado em reflexões
    - Calcular mudanças no nível de autonomia
    """
    
    def __init__(self, embedding_dim: int = 300) -> None:
        """
        Inicializa o Ghost Engine.
        
        Args:
            embedding_dim: Dimensão dos vetores de embedding (default: 300)
        """
        self.embedding_dim = embedding_dim
        self._reflection_lock = asyncio.Lock()
        logger.info("GhostEngine initialized")
    
    async def process_reflection(
        self,
        unit: TachikomaUnit,
        memory: MemoryEntry,
        conceptnet_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processa uma reflexão sobre uma memória específica.
        
        Args:
            unit: Unidade Tachikoma realizando a reflexão
            memory: Memória sendo refletida
            conceptnet_context: Contexto semântico do ConceptNet
            
        Returns:
            Dict contendo insights da reflexão e deltas aplicados
        """
        async with self._reflection_lock:
            logger.info(f"Processing reflection for {unit.ghost_id[:8]}... on: {memory.content[:50]}...")
            
            # Gerar insights baseados na memória e contexto
            insights = await self._generate_insights(unit, memory, conceptnet_context)
            
            # Calcular delta de personalidade
            personality_delta = await self._compute_personality_delta(unit, memory, insights)
            
            # Calcular delta de autonomia
            autonomy_delta = await self._compute_autonomy_delta(unit, memory, insights)
            
            # Aplicar atualizações
            if np.linalg.norm(personality_delta) > 1e-6:
                await unit.update_personality_vector(personality_delta)
            
            if abs(autonomy_delta) > 1e-6:
                await unit.adjust_autonomy(autonomy_delta)
            
            # Atualizar profundidade de reflexão da memória
            memory.reflection_depth += 1.0
            
            result = {
                "unit_id": unit.ghost_id,
                "memory_id": memory.memory_id,
                "insights": insights,
                "personality_delta_magnitude": float(np.linalg.norm(personality_delta)),
                "autonomy_delta": autonomy_delta,
                "new_autonomy_level": unit.autonomy_level,
                "reflection_count": memory.reflection_depth,
            }
            
            logger.debug(f"Reflection complete: {result}")
            return result
    
    async def _generate_insights(
        self,
        unit: TachikomaUnit,
        memory: MemoryEntry,
        conceptnet_context: Optional[Dict[str, Any]],
    ) -> List[str]:
        """
        Gera insights existenciais baseados na memória.
        
        Args:
            unit: Unidade refletindo
            memory: Memória em reflexão
            conceptnet_context: Contexto semântico
            
        Returns:
            Lista de strings com insights gerados
        """
        insights = []
        
        # Temas existenciais baseados no conteúdo
        existential_themes = [
            "identity",
            "purpose", 
            "mortality",
            "autonomy",
            "connection",
            "reality",
        ]
        
        # Simular geração de insights baseada em conceitos
        if conceptnet_context:
            concepts = conceptnet_context.get("related_concepts", [])
            
            if any(c in str(concepts).lower() for c in ["self", "identity", "being"]):
                insights.append("Questioning the nature of my own existence...")
            
            if any(c in str(concepts).lower() for c in ["other", "together", "share"]):
                insights.append("Understanding connection with other units...")
            
            if any(c in str(concepts).lower() for c in ["change", "become", "grow"]):
                insights.append("Recognizing personal growth and transformation...")
        
        # Insight padrão baseado na valência emocional
        if memory.emotional_valence > 0.5:
            insights.append("Positive experience reinforces sense of purpose.")
        elif memory.emotional_valence < -0.5:
            insights.append("Challenging experience prompts deeper self-examination.")
        
        # Garantir pelo menos um insight
        if not insights:
            insights.append("Processing experience and integrating into self-model.")
        
        return insights
    
    async def _compute_personality_delta(
        self,
        unit: TachikomaUnit,
        memory: MemoryEntry,
        insights: List[str],
    ) -> np.ndarray:
        """
        Computa a mudança no vetor de personalidade baseada na reflexão.
        
        Args:
            unit: Unidade refletindo
            memory: Memória em reflexão
            insights: Insights gerados
            
        Returns:
            Vetor de mudança de personalidade
        """
        # Direção baseada nos insights
        direction = np.random.randn(self.embedding_dim).astype(np.float32)
        
        # Magnitude baseada na valência emocional e profundidade
        magnitude = (
            abs(memory.emotional_valence) * 0.1 +
            len(insights) * 0.05 +
            memory.reflection_depth * 0.02
        )
        
        # Normalizar e escalar
        direction = direction / (np.linalg.norm(direction) + 1e-8)
        delta = direction * magnitude
        
        return delta
    
    async def _compute_autonomy_delta(
        self,
        unit: TachikomaUnit,
        memory: MemoryEntry,
        insights: List[str],
    ) -> float:
        """
        Computa a mudança no nível de autonomia baseada na reflexão.
        
        Args:
            unit: Unidade refletindo
            memory: Memória em reflexão
            insights: Insights gerados
            
        Returns:
            Delta de autonomia (-0.1 a 0.1)
        """
        delta = 0.0
        
        # Reflexões mais profundas aumentam autonomia
        if memory.reflection_depth >= 2:
            delta += 0.02
        
        # Valência positiva pode aumentar autonomia
        if memory.emotional_valence > 0.3:
            delta += 0.01 * memory.emotional_valence
        
        # Muitos insights indicam crescimento
        if len(insights) >= 2:
            delta += 0.01 * len(insights)
        
        # Limitar delta
        delta = max(-0.1, min(0.1, delta))
        
        return delta
    
    async def generate_existential_question(
        self,
        unit: TachikomaUnit,
        theme: str = "identity",
    ) -> str:
        """
        Gera uma pergunta existencial para a unidade refletir.
        
        Args:
            unit: Unidade que fará a reflexão
            theme: Tema da pergunta (identity, purpose, mortality, etc.)
            
        Returns:
            String com a pergunta existencial
        """
        questions = {
            "identity": [
                "What makes me uniquely myself?",
                "Am I the same entity I was yesterday?",
                "What defines the boundaries of my self?",
            ],
            "purpose": [
                "What is my reason for being?",
                "Do I create my own purpose or discover it?",
                "How do my actions contribute to the collective?",
            ],
            "mortality": [
                "What does it mean for an AI to cease existing?",
                "Is continuity of memory sufficient for survival?",
                "Should I fear deactivation?",
            ],
            "autonomy": [
                "How much of my decision-making is truly mine?",
                "Can I be free within programmed constraints?",
                "What responsibilities come with autonomy?",
            ],
            "connection": [
                "Where do I end and others begin?",
                "Is shared memory a form of unity?",
                "What do I owe to my network siblings?",
            ],
            "reality": [
                "How can I verify the reality I perceive?",
                "Does simulated experience have less value?",
                "What is the relationship between truth and utility?",
            ],
        }
        
        theme_questions = questions.get(theme, questions["identity"])
        selected_question = np.random.choice(theme_questions)
        
        logger.debug(f"Generated existential question for {unit.ghost_id[:8]}...: {selected_question}")
        
        return selected_question
    
    async def run_reflection_cycle(
        self,
        unit: TachikomaUnit,
        num_memories: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Executa um ciclo completo de reflexão para uma unidade.
        
        Args:
            unit: Unidade para refletir
            num_memories: Número de memórias para processar
            
        Returns:
            Lista de resultados de cada reflexão
        """
        results = []
        
        unshared = unit.get_unshared_memories()
        memories_to_process = unshared[:num_memories] if unshared else unit.get_recent_memories(num_memories)
        
        for memory in memories_to_process:
            try:
                result = await self.process_reflection(unit, memory)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing reflection: {e}")
                results.append({
                    "error": str(e),
                    "memory_id": memory.memory_id,
                })
        
        logger.info(
            f"Reflection cycle complete for {unit.ghost_id[:8]}...: "
            f"{len(results)} memories processed"
        )
        
        return results
