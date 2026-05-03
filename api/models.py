"""Pydantic models for API requests/responses."""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class ExperienceInput(BaseModel):
    """Input model for experience registration."""
    content: str = Field(..., description="Experience content")
    shareable: bool = Field(True, description="Whether to share with collective")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MemoryResponse(BaseModel):
    """Response model for memory queries."""
    memory_id: str
    content: str
    concepts: List[str]
    valence: float
    timestamp: str
    score: Optional[float] = None

class TachikomaState(BaseModel):
    """State model for Tachikoma unit."""
    ghost_id: str
    personality_vector: List[float]
    autonomy_level: float
    trust_score: float
    unique_experience_count: int
    shared_experience_count: int
    last_sync_timestamp: Optional[str] = None

class ReflectionResult(BaseModel):
    """Result model for reflection cycle."""
    tachikoma_id: str
    timestamp: str
    questions_generated: int
    insights: List[Dict[str, Any]]
    autonomy_delta: float
    reflection_depth: int
