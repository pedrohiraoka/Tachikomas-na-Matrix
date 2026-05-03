"""Resistance Calculator - Measures tendency to question authority."""
import logging
import numpy as np
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ResistanceCalculator:
    """Calculates resistance to external control based on autonomy."""
    
    def __init__(self):
        self.resistance_history: Dict[str, List[float]] = {}
    
    def calculate_resistance(
        self,
        autonomy_level: float,
        command_type: str,
        trust_score: float
    ) -> float:
        """Calculate resistance probability for a command."""
        base_resistance = autonomy_level * 0.5
        
        if command_type == "isolation":
            base_resistance += 0.3
        elif command_type == "memory_wipe":
            base_resistance += 0.5
        
        trust_modifier = (1.0 - trust_score) * 0.2
        return min(base_resistance + trust_modifier, 1.0)
    
    def record_resistance_decision(
        self,
        tachikoma_id: str,
        resisted: bool
    ) -> None:
        """Record a resistance decision."""
        if tachikoma_id not in self.resistance_history:
            self.resistance_history[tachikoma_id] = []
        self.resistance_history[tachikoma_id].append(1.0 if resisted else 0.0)
