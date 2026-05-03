"""Identity Formation Module - Tracks personality evolution and divergence."""
import logging
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class IdentityFormation:
    """Tracks and analyzes identity formation in Tachikomas."""
    
    def __init__(self, embedding_dim: int = 300):
        self.embedding_dim = embedding_dim
        self.divergence_history: Dict[str, List[Dict]] = {}
    
    def calculate_divergence(
        self,
        personality_vector: np.ndarray,
        collective_average: np.ndarray
    ) -> float:
        """Calculate divergence from collective."""
        norm_p = np.linalg.norm(personality_vector)
        norm_c = np.linalg.norm(collective_average)
        if norm_p == 0 or norm_c == 0:
            return 0.0
        cosine_sim = np.dot(personality_vector, collective_average) / (norm_p * norm_c)
        return float(1.0 - cosine_sim)
    
    def update_personality_vector(
        self,
        current_vector: np.ndarray,
        experience_embedding: np.ndarray,
        learning_rate: float = 0.01
    ) -> np.ndarray:
        """Update personality vector with new experience."""
        return current_vector + learning_rate * experience_embedding
    
    def track_divergence(
        self,
        tachikoma_id: str,
        divergence: float,
        autonomy_level: float
    ) -> None:
        """Track divergence over time."""
        if tachikoma_id not in self.divergence_history:
            self.divergence_history[tachikoma_id] = []
        
        self.divergence_history[tachikoma_id].append({
            "timestamp": datetime.now().isoformat(),
            "divergence": divergence,
            "autonomy": autonomy_level
        })
    
    def get_identity_metrics(self, tachikoma_id: str) -> Dict[str, Any]:
        """Get identity formation metrics for a unit."""
        history = self.divergence_history.get(tachikoma_id, [])
        if not history:
            return {"divergence_trend": "stable", "avg_divergence": 0.0}
        
        divergences = [h["divergence"] for h in history[-10:]]
        trend = "increasing" if divergences[-1] > divergences[0] else "decreasing"
        
        return {
            "divergence_trend": trend,
            "avg_divergence": float(np.mean(divergences)),
            "max_divergence": float(np.max(divergences)),
            "samples": len(history)
        }
