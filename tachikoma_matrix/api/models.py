"""
API Models - Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ExperienceRequest(BaseModel):
    """Request model for posting experience."""
    
    content: str = Field(..., description="Content of the experience")
    shareable: bool = Field(default=True, description="Whether to share with network")
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ReflectionResponse(BaseModel):
    """Response model for reflection endpoint."""
    
    unit_id: str
    memory_id: str
    insights: List[str]
    personality_delta_magnitude: float
    autonomy_delta: float
    new_autonomy_level: float
    reflection_count: int


class TachikomaState(BaseModel):
    """State model for a Tachikoma unit."""
    
    ghost_id: str
    hardware_signature: str
    personality_vector: List[float]
    autonomy_level: float
    trust_score: float
    last_sync_timestamp: Optional[str]
    unique_experience_count: int
    shared_experience_count: int
    local_memory_count: int


class NetworkStatus(BaseModel):
    """Network status model."""
    
    total_units: int
    average_autonomy: float
    average_trust: float
    total_memories: int
    status_distribution: Dict[str, int]
    network_status: str
    timestamp: str


class CollectiveMemoryResult(BaseModel):
    """Result model for collective memory search."""
    
    memory_id: str
    content: str
    source_unit_id: str
    timestamp: str
    similarity: float
    conceptnet_concepts: List[str]


class WebSocketEvent(BaseModel):
    """WebSocket event model."""
    
    event_type: str
    data: Dict[str, Any]
    timestamp: str
