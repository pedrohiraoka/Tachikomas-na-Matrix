"""Mortality Model - Simulates Tachikoma awareness of termination."""
import logging
import numpy as np
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MortalityModel:
    """Models Tachikoma awareness of mortality and finitude."""
    
    def __init__(self):
        self.termination_events: Dict[str, Dict] = {}
    
    def record_termination(self, tachikoma_id: str, reason: str) -> None:
        """Record a termination event for collective memory."""
        self.termination_events[tachikoma_id] = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason
        }
    
    def compute_mortality_salience(
        self,
        autonomy_level: float,
        reflection_count: int
    ) -> float:
        """Compute mortality salience based on autonomy and reflection."""
        base_salience = 0.1
        autonomy_factor = autonomy_level * 0.3
        reflection_factor = min(reflection_count * 0.02, 0.3)
        return min(base_salience + autonomy_factor + reflection_factor, 1.0)
    
    def generate_mortality_reflection(self, salience: float) -> Optional[str]:
        """Generate mortality-related reflection prompt."""
        if salience < 0.3:
            return None
        
        prompts = [
            "What persists when I am no longer active?",
            "How do my contributions to the collective outlast me?",
            "Is termination an end or a transformation?",
            "What meaning does finitude give to my existence?"
        ]
        return np.random.choice(prompts)
