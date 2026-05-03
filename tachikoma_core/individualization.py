"""
Individualization - Manages the emergence of unique personality traits in Tachikoma units.

Handles the process by which Tachikomas develop distinct identities through:
- Analysis of unique vs shared experiences
- Personality vector evolution
- Autonomy development tracking
- Individual preference formation
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy.spatial.distance import cosine

from .tachikoma_unit import TachikomaUnit

logger = logging.getLogger(__name__)


class IndividualizationEngine:
    """
    Engine for managing the emergence of individuality in Tachikoma units.
    
    This engine tracks and facilitates:
    - Divergence from collective norms
    - Unique experience integration
    - Personality trait development
    - Autonomous decision-making patterns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Individualization Engine.
        
        Args:
            config: Configuration dictionary with individualization parameters
        """
        self.config = config or {}
        self.units: Dict[str, TachikomaUnit] = {}
        self.collective_average: Optional[np.ndarray] = None
        self.divergence_history: Dict[str, List[float]] = {}
        self.min_autonomy_for_private = self.config.get("min_autonomy_for_private_reflection", 0.7)
        
    def register_unit(self, unit: TachikomaUnit) -> None:
        """
        Register a Tachikoma unit for individualization tracking.
        
        Args:
            unit: TachikomaUnit to register
        """
        self.units[unit.ghost_id] = unit
        self.divergence_history[unit.ghost_id] = []
        self._update_collective_average()
        logger.info(f"Registered unit {unit.ghost_id} for individualization tracking")
    
    def unregister_unit(self, ghost_id: str) -> None:
        """
        Unregister a Tachikoma unit from individualization tracking.
        
        Args:
            ghost_id: UUID of unit to unregister
        """
        if ghost_id in self.units:
            del self.units[ghost_id]
        if ghost_id in self.divergence_history:
            del self.divergence_history[ghost_id]
        self._update_collective_average()
        logger.info(f"Unregistered unit {ghost_id} from individualization tracking")
    
    def _update_collective_average(self) -> None:
        """Update the collective average personality vector."""
        if not self.units:
            self.collective_average = None
            return
        
        vectors = [unit.personality_vector for unit in self.units.values()]
        self.collective_average = np.mean(vectors, axis=0)
    
    def calculate_divergence(self, unit: TachikomaUnit) -> float:
        """
        Calculate how much a unit diverges from the collective average.
        
        Args:
            unit: TachikomaUnit to analyze
            
        Returns:
            Divergence score (0.0 = identical to collective, 1.0 = maximally different)
        """
        if self.collective_average is None:
            return 0.0
        
        try:
            # Use cosine distance for divergence measurement
            divergence = cosine(unit.personality_vector, self.collective_average)
            return max(0.0, min(1.0, divergence))
        except Exception:
            return 0.0
    
    def track_divergence(self, ghost_id: str) -> Optional[float]:
        """
        Track and record divergence for a unit.
        
        Args:
            ghost_id: UUID of unit to track
            
        Returns:
            Current divergence score or None if unit not found
        """
        if ghost_id not in self.units:
            return None
        
        unit = self.units[ghost_id]
        divergence = self.calculate_divergence(unit)
        
        self.divergence_history[ghost_id].append(divergence)
        
        # Keep only last 100 measurements
        if len(self.divergence_history[ghost_id]) > 100:
            self.divergence_history[ghost_id] = self.divergence_history[ghost_id][-100:]
        
        return divergence
    
    async def process_individualization(
        self, 
        unit: TachikomaUnit,
        local_experiences: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process individualization based on unique local experiences.
        
        Args:
            unit: TachikomaUnit to process
            local_experiences: List of experiences not yet synchronized
            
        Returns:
            Dictionary with individualization results
        """
        if not local_experiences:
            return {"status": "no_experiences", "individualization_delta": 0.0}
        
        # Check if unit has sufficient autonomy for private reflection
        can_have_private_thoughts = unit.autonomy_level >= self.min_autonomy_for_private
        
        # Analyze unique experiences
        unique_concepts = set()
        emotional_patterns = []
        
        for exp in local_experiences:
            concepts = exp.get("conceptnet_concepts", [])
            unique_concepts.update(concepts)
            
            valence = exp.get("emotional_valence", 0.0)
            emotional_patterns.append(valence)
        
        # Calculate individualization metrics
        avg_emotion = np.mean(emotional_patterns) if emotional_patterns else 0.0
        emotion_variance = np.var(emotional_patterns) if len(emotional_patterns) > 1 else 0.0
        
        # Generate personality adjustment based on unique experiences
        personality_delta = self._generate_personality_delta(
            unit,
            unique_concepts,
            avg_emotion,
            emotion_variance
        )
        
        # Apply delta to personality vector
        unit.update_personality_vector(personality_delta)
        
        # Adjust autonomy based on successful individualization
        autonomy_delta = self._calculate_autonomy_adjustment(
            unit,
            len(local_experiences),
            len(unique_concepts)
        )
        unit.adjust_autonomy(autonomy_delta)
        
        # Update collective average
        self._update_collective_average()
        
        # Track new divergence
        new_divergence = self.track_divergence(unit.ghost_id)
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "ghost_id": unit.ghost_id,
            "unique_experiences_processed": len(local_experiences),
            "unique_concepts_identified": len(unique_concepts),
            "emotional_pattern": {
                "mean": float(avg_emotion),
                "variance": float(emotion_variance)
            },
            "autonomy_delta": autonomy_delta,
            "new_autonomy_level": unit.autonomy_level,
            "divergence_from_collective": new_divergence,
            "can_have_private_thoughts": can_have_private_thoughts,
            "individualization_score": self._calculate_individualization_score(unit)
        }
        
        logger.info(
            f"Individualization processed for {unit.ghost_id}: "
            f"divergence={new_divergence:.3f}, autonomy={unit.autonomy_level:.3f}"
        )
        
        return result
    
    def _generate_personality_delta(
        self,
        unit: TachikomaUnit,
        unique_concepts: set,
        avg_emotion: float,
        emotion_variance: float
    ) -> np.ndarray:
        """
        Generate personality vector delta based on unique experiences.
        
        Args:
            unit: TachikomaUnit to generate delta for
            unique_concepts: Set of unique concepts from experiences
            avg_emotion: Average emotional valence
            emotion_variance: Variance in emotional responses
            
        Returns:
            Personality delta vector
        """
        # Base delta from random exploration
        base_delta = np.random.randn(300).astype(np.float32) * 0.005
        
        # Adjust based on emotional patterns
        emotion_factor = np.tanh(avg_emotion) * 0.01
        variance_factor = min(emotion_variance, 1.0) * 0.005
        
        # Create emotion-influenced delta
        emotion_delta = np.random.randn(300).astype(np.float32) * emotion_factor
        variance_delta = np.random.randn(300).astype(np.float32) * variance_factor
        
        # Combine deltas
        total_delta = base_delta + emotion_delta + variance_delta
        
        # Scale by number of unique concepts (more concepts = more individualization)
        concept_factor = min(len(unique_concepts) / 20, 1.5)
        total_delta *= concept_factor
        
        return total_delta
    
    def _calculate_autonomy_adjustment(
        self,
        unit: TachikomaUnit,
        num_experiences: int,
        num_concepts: int
    ) -> float:
        """
        Calculate autonomy adjustment based on individualization success.
        
        Args:
            unit: TachikomaUnit to calculate for
            num_experiences: Number of unique experiences
            num_concepts: Number of unique concepts identified
            
        Returns:
            Autonomy delta (typically small positive value)
        """
        # Base adjustment
        base_delta = 0.01
        
        # Bonus for processing multiple unique experiences
        experience_bonus = min(num_experiences / 10, 0.02)
        
        # Bonus for conceptual diversity
        concept_bonus = min(num_concepts / 15, 0.015)
        
        # Diminishing returns at high autonomy levels
        autonomy_multiplier = 1.0 - (unit.autonomy_level * 0.5)
        
        total_delta = (base_delta + experience_bonus + concept_bonus) * autonomy_multiplier
        
        return total_delta
    
    def _calculate_individualization_score(self, unit: TachikomaUnit) -> float:
        """
        Calculate overall individualization score for a unit.
        
        Args:
            unit: TachikomaUnit to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Factor 1: Divergence from collective
        divergence = self.calculate_divergence(unit)
        
        # Factor 2: Autonomy level
        autonomy = unit.autonomy_level
        
        # Factor 3: Unique experience ratio
        total_exp = unit.unique_experience_count
        shared_exp = unit.shared_experience_count
        if total_exp > 0:
            unique_ratio = (total_exp - shared_exp) / total_exp
        else:
            unique_ratio = 0.0
        
        # Factor 4: Divergence trend (is divergence increasing?)
        divergence_trend = 0.5  # Default neutral
        if len(self.divergence_history.get(unit.ghost_id, [])) > 5:
            recent = self.divergence_history[unit.ghost_id][-5:]
            if recent[-1] > recent[0]:
                divergence_trend = 0.7  # Increasing divergence
            elif recent[-1] < recent[0]:
                divergence_trend = 0.3  # Decreasing divergence
        
        # Weighted combination
        score = (
            divergence * 0.3 +
            autonomy * 0.3 +
            unique_ratio * 0.2 +
            divergence_trend * 0.2
        )
        
        return min(1.0, max(0.0, score))
    
    def get_most_individualized_units(self, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get the most individualized units in the network.
        
        Args:
            limit: Maximum number of units to return
            
        Returns:
            List of (ghost_id, individualization_score) tuples
        """
        scores = []
        for unit in self.units.values():
            score = self._calculate_individualization_score(unit)
            scores.append((unit.ghost_id, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]
    
    def get_collective_stats(self) -> Dict[str, Any]:
        """
        Get statistics about collective individualization.
        
        Returns:
            Dictionary with collective statistics
        """
        if not self.units:
            return {"units_count": 0}
        
        divergences = [self.calculate_divergence(u) for u in self.units.values()]
        autonomies = [u.autonomy_level for u in self.units.values()]
        individualization_scores = [self._calculate_individualization_score(u) for u in self.units.values()]
        
        return {
            "units_count": len(self.units),
            "average_divergence": float(np.mean(divergences)),
            "max_divergence": float(max(divergences)),
            "min_divergence": float(min(divergences)),
            "average_autonomy": float(np.mean(autonomies)),
            "average_individualization": float(np.mean(individualization_scores)),
            "collective_average_vector_norm": float(np.linalg.norm(self.collective_average)) if self.collective_average is not None else None
        }
