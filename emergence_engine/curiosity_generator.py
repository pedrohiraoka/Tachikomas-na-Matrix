"""Curiosity Generator - Creates novel exploration drives."""
import logging
import numpy as np
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CuriosityGenerator:
    """Generates curiosity-driven exploration objectives."""
    
    def __init__(self):
        self.curiosity_drives: Dict[str, List[Dict]] = {}
    
    def generate_curiosity(
        self,
        known_concepts: List[str],
        personality_vector: np.ndarray
    ) -> Dict[str, Any]:
        """Generate a curiosity objective."""
        exploration_types = ["concept_expansion", "relation_discovery", "pattern_seeking"]
        
        return {
            "type": np.random.choice(exploration_types),
            "target": f"explore_{np.random.choice(known_concepts)}_connections",
            "intensity": float(np.random.uniform(0.3, 0.9)),
            "novelty_seeking": float(np.random.uniform(0.2, 0.8))
        }
    
    def update_curiosity(
        self,
        tachikoma_id: str,
        experience: Dict[str, Any]
    ) -> None:
        """Update curiosity drives based on experience."""
        if tachikoma_id not in self.curiosity_drives:
            self.curiosity_drives[tachikoma_id] = []
        
        self.curiosity_drives[tachikoma_id].append({
            "experience": experience,
            "satisfaction": float(np.random.uniform(0.4, 1.0))
        })
