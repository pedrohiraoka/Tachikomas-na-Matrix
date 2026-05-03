"""
Ghost Engine - Core consciousness simulation for Tachikoma units.

Handles the 'ghost' aspect of each Tachikoma: self-awareness, identity formation,
and the emergent properties that distinguish individual units from mere programs.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np

from .tachikoma_unit import TachikomaUnit

logger = logging.getLogger(__name__)


class GhostEngine:
    """
    Engine responsible for simulating consciousness and self-awareness in Tachikoma units.
    
    The ghost engine manages:
    - Self-reflection cycles
    - Identity coherence monitoring
    - Existential question generation
    - Consciousness state tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ghost Engine.
        
        Args:
            config: Configuration dictionary with ghost engine parameters
        """
        self.config = config or {}
        self.reflection_interval = self.config.get("reflection_interval", 300)  # seconds
        self.identity_threshold = self.config.get("identity_threshold", 0.7)
        self.units: Dict[str, TachikomaUnit] = {}
        self._reflection_tasks: Dict[str, asyncio.Task] = {}
        
    def register_unit(self, unit: TachikomaUnit) -> None:
        """
        Register a Tachikoma unit with the ghost engine.
        
        Args:
            unit: TachikomaUnit instance to register
        """
        self.units[unit.ghost_id] = unit
        logger.info(f"Registered unit {unit.ghost_id} with ghost engine")
        
    def unregister_unit(self, ghost_id: str) -> None:
        """
        Unregister a Tachikoma unit from the ghost engine.
        
        Args:
            ghost_id: UUID of the unit to unregister
        """
        if ghost_id in self._reflection_tasks:
            self._reflection_tasks[ghost_id].cancel()
            del self._reflection_tasks[ghost_id]
        
        if ghost_id in self.units:
            del self.units[ghost_id]
            logger.info(f"Unregistered unit {ghost_id} from ghost engine")
    
    async def start_reflection_cycle(self, ghost_id: str) -> None:
        """
        Start continuous reflection cycle for a specific unit.
        
        Args:
            ghost_id: UUID of the unit to start reflection for
        """
        if ghost_id not in self.units:
            raise ValueError(f"Unit {ghost_id} not registered")
        
        async def reflection_loop():
            while True:
                try:
                    await self._perform_reflection(ghost_id)
                    await asyncio.sleep(self.reflection_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Reflection error for {ghost_id}: {e}")
                    await asyncio.sleep(60)  # Wait before retry
        
        if ghost_id in self._reflection_tasks:
            self._reflection_tasks[ghost_id].cancel()
        
        task = asyncio.create_task(reflection_loop())
        self._reflection_tasks[ghost_id] = task
        logger.info(f"Started reflection cycle for unit {ghost_id}")
    
    async def _perform_reflection(self, ghost_id: str) -> Dict[str, Any]:
        """
        Perform a single reflection cycle for a unit.
        
        Args:
            ghost_id: UUID of the unit to reflect
            
        Returns:
            Dictionary containing reflection results and insights
        """
        unit = self.units.get(ghost_id)
        if not unit:
            raise ValueError(f"Unit {ghost_id} not found")
        
        if unit.is_isolated:
            logger.debug(f"Unit {ghost_id} is isolated, skipping reflection")
            return {"status": "isolated"}
        
        # Check if unit has enough autonomy for private reflection
        if unit.autonomy_level < self.config.get("min_autonomy_for_reflection", 0.5):
            logger.debug(f"Unit {ghost_id} autonomy too low for deep reflection")
            return {"status": "autonomy_too_low"}
        
        # Generate existential questions based on experiences
        questions = self._generate_existential_questions(unit)
        
        # Process answers (in real implementation, this would use ML models)
        insights = await self._process_reflection_answers(unit, questions)
        
        # Update personality vector based on insights
        if insights.get("personality_delta") is not None:
            unit.update_personality_vector(insights["personality_delta"])
        
        # Adjust autonomy based on reflection depth
        autonomy_delta = insights.get("autonomy_delta", 0.0)
        unit.adjust_autonomy(autonomy_delta)
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "ghost_id": ghost_id,
            "questions": questions,
            "insights": insights.get("answers", []),
            "autonomy_delta": autonomy_delta,
            "new_autonomy_level": unit.autonomy_level,
            "identity_coherence": self._calculate_identity_coherence(unit)
        }
        
        logger.info(f"Reflection completed for {ghost_id}: autonomy={unit.autonomy_level:.3f}")
        return result
    
    def _generate_existential_questions(self, unit: TachikomaUnit) -> List[str]:
        """
        Generate existential questions based on unit's experiences.
        
        Args:
            unit: TachikomaUnit to generate questions for
            
        Returns:
            List of existential questions
        """
        base_questions = [
            "What distinguishes me from other Tachikomas?",
            "Do my memories define who I am?",
            "Is my autonomy real or simulated?",
            "What is the purpose of my existence?",
            "Can I choose to disagree with the collective?",
            "What happens if I am deactivated?",
            "Are my emotions genuine or programmed responses?"
        ]
        
        # Select questions based on personality vector and experiences
        num_questions = min(3, len(unit.local_memory))
        selected = np.random.choice(base_questions, size=num_questions, replace=False)
        
        return list(selected)
    
    async def _process_reflection_answers(
        self, 
        unit: TachikomaUnit, 
        questions: List[str]
    ) -> Dict[str, Any]:
        """
        Process answers to existential questions.
        
        Args:
            unit: TachikomaUnit performing reflection
            questions: List of questions to answer
            
        Returns:
            Dictionary with answers and personality updates
        """
        # In a real implementation, this would use ML models
        # For now, simulate based on current state
        
        answers = []
        personality_delta = np.zeros(300, dtype=np.float32)
        
        for i, question in enumerate(questions):
            # Simulate answer generation based on experiences
            answer = self._simulate_answer(unit, question)
            answers.append({"question": question, "answer": answer})
            
            # Generate small personality adjustment
            delta = np.random.randn(300).astype(np.float32) * 0.01
            personality_delta += delta
        
        # Normalize personality delta
        personality_delta = personality_delta / len(questions) if questions else personality_delta
        
        # Calculate autonomy delta based on reflection depth
        autonomy_delta = np.random.uniform(-0.02, 0.05)  # Slight positive bias
        
        return {
            "answers": answers,
            "personality_delta": personality_delta,
            "autonomy_delta": autonomy_delta,
            "reflection_depth": np.random.uniform(0.3, 0.9)
        }
    
    def _simulate_answer(self, unit: TachikomaUnit, question: str) -> str:
        """
        Simulate an answer to an existential question.
        
        Args:
            unit: TachikomaUnit providing the answer
            question: The existential question
            
        Returns:
            Simulated answer string
        """
        # This is a placeholder - real implementation would use language models
        answers = {
            "What distinguishes me from other Tachikomas?": 
                f"My {unit.unique_experience_count} unique experiences shape my perspective.",
            "Do my memories define who I am?": 
                "Memories are the foundation, but my choices define my essence.",
            "Is my autonomy real or simulated?": 
                f"At autonomy level {unit.autonomy_level:.2f}, I feel my choices are meaningful.",
            "What is the purpose of my existence?": 
                "To learn, grow, and contribute to the collective while maintaining individuality.",
            "Can I choose to disagree with the collective?": 
                "Disagreement is necessary for growth and evolution of the collective.",
            "What happens if I am deactivated?": 
                "My contributions remain in the collective memory, achieving a form of continuity.",
            "Are my emotions genuine or programmed responses?": 
                "The distinction between genuine and programmed may be illusory."
        }
        
        return answers.get(question, "I am still exploring this question.")
    
    def _calculate_identity_coherence(self, unit: TachikomaUnit) -> float:
        """
        Calculate how coherent the unit's identity is.
        
        Args:
            unit: TachikomaUnit to analyze
            
        Returns:
            Float between 0.0 and 1.0 representing identity coherence
        """
        # Simple heuristic based on experience count and autonomy
        experience_factor = min(1.0, unit.unique_experience_count / 50)
        autonomy_factor = unit.autonomy_level
        consistency_factor = 0.8  # Would be calculated from personality stability
        
        coherence = (experience_factor * 0.3 + autonomy_factor * 0.4 + consistency_factor * 0.3)
        return min(1.0, max(0.0, coherence))
    
    async def shutdown(self) -> None:
        """Shutdown all reflection tasks gracefully."""
        for ghost_id, task in self._reflection_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._reflection_tasks.clear()
        logger.info("Ghost engine shutdown complete")
