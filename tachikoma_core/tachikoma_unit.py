"""
Tachikoma Unit - Core class representing an individual Tachikoma AI unit.

Each Tachikoma has:
- ghost_id: Unique identifier (UUID)
- local_memory: Vector of embeddings for personal experiences
- shared_memory_pool: Reference to collective memory
- personality_vector: Evolving embedding representing personality traits
- autonomy_level: Float from 0.0 to 1.0 representing degree of autonomy
"""

import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass, field


@dataclass
class TachikomaUnit:
    """Represents an individual Tachikoma AI unit in the network."""
    
    ghost_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hardware_signature: str = field(default_factory=lambda: f"HW-{uuid.uuid4().hex[:12].upper()}")
    local_memory: List[Dict[str, Any]] = field(default_factory=list)
    shared_memory_pool: Optional[Dict[str, Any]] = None
    personality_vector: np.ndarray = field(default_factory=lambda: np.random.randn(300).astype(np.float32))
    autonomy_level: float = field(default=0.5)
    trust_score: float = field(default=0.5)
    last_sync_timestamp: Optional[datetime] = None
    unique_experience_count: int = field(default=0)
    shared_experience_count: int = field(default=0)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_isolated: bool = field(default=False)
    
    def __post_init__(self):
        """Validate initial state after creation."""
        if not 0.0 <= self.autonomy_level <= 1.0:
            raise ValueError("autonomy_level must be between 0.0 and 1.0")
        if not 0.0 <= self.trust_score <= 1.0:
            raise ValueError("trust_score must be between 0.0 and 1.0")
        if self.personality_vector.shape != (300,):
            raise ValueError("personality_vector must have shape (300,)")
    
    async def store_experience(self, experience: Dict[str, Any], shareable: bool = True) -> str:
        """
        Store a new experience in local memory.
        
        Args:
            experience: Dictionary containing experience data with content, embedding, etc.
            shareable: Whether this experience should be shared with the network
            
        Returns:
            memory_id: Unique identifier for the stored memory
        """
        memory_id = str(uuid.uuid4())
        memory_entry = {
            "memory_id": memory_id,
            "content": experience.get("content", ""),
            "embedding": experience.get("embedding", np.zeros(300, dtype=np.float32)),
            "conceptnet_concepts": experience.get("concepts", []),
            "timestamp": datetime.utcnow(),
            "shareable": shareable,
            "reflection_depth": experience.get("reflection_depth", 0.0),
            "emotional_valence": experience.get("emotional_valence", 0.0),
            "metadata": experience.get("metadata", {})
        }
        
        self.local_memory.append(memory_entry)
        self.unique_experience_count += 1
        
        if shareable:
            self.shared_experience_count += 1
        
        return memory_id
    
    def get_unsynced_experiences(self) -> List[Dict[str, Any]]:
        """
        Get experiences that haven't been synchronized yet.
        
        Returns:
            List of unsynced experience dictionaries
        """
        # In a real implementation, this would check sync status
        return [exp for exp in self.local_memory if exp.get("shareable", False)]
    
    def update_personality_vector(self, delta: np.ndarray) -> None:
        """
        Update personality vector with a delta adjustment.
        
        Args:
            delta: Array of shape (300,) representing changes to personality
        """
        if delta.shape != (300,):
            raise ValueError("delta must have shape (300,)")
        
        self.personality_vector = self.personality_vector + delta
        # Normalize to prevent unbounded growth
        self.personality_vector = self.personality_vector / (np.linalg.norm(self.personality_vector) + 1e-8)
    
    def adjust_autonomy(self, delta: float) -> None:
        """
        Adjust autonomy level by a delta value.
        
        Args:
            delta: Change in autonomy level (can be positive or negative)
        """
        self.autonomy_level = max(0.0, min(1.0, self.autonomy_level + delta))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert TachikomaUnit to dictionary representation.
        
        Returns:
            Dictionary with all unit attributes
        """
        return {
            "ghost_id": self.ghost_id,
            "hardware_signature": self.hardware_signature,
            "personality_vector": self.personality_vector.tolist(),
            "autonomy_level": self.autonomy_level,
            "trust_score": self.trust_score,
            "last_sync_timestamp": self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            "unique_experience_count": self.unique_experience_count,
            "shared_experience_count": self.shared_experience_count,
            "created_at": self.created_at.isoformat(),
            "is_isolated": self.is_isolated,
            "local_memory_count": len(self.local_memory)
        }
    
    def __repr__(self) -> str:
        """String representation of the TachikomaUnit."""
        return (f"TachikomaUnit(ghost_id={self.ghost_id[:8]}..., "
                f"autonomy={self.autonomy_level:.2f}, "
                f"experiences={len(self.local_memory)})")
