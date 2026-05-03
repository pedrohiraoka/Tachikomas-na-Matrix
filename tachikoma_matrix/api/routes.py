"""
API Routes - FastAPI route definitions.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["tachikoma"])


# Mock data for demonstration
_units: Dict[str, Any] = {}
_shared_memories: List[Dict[str, Any]] = []


@router.post("/tachikomas/{tachikoma_id}/experience")
async def post_experience(
    tachikoma_id: str,
    content: str,
    shareable: bool = True,
    emotional_valence: float = 0.0,
) -> Dict[str, Any]:
    """
    Register a new experience for a Tachikoma unit.
    
    - Creates embedding
    - Stores memory
    - Triggers sync if shareable
    """
    logger.info(f"Experience posted for {tachikoma_id}: {content[:50]}...")
    
    # Create mock memory entry
    memory = {
        "memory_id": f"mem-{len(_shared_memories) + 1}",
        "tachikoma_id": tachikoma_id,
        "content": content,
        "shareable": shareable,
        "emotional_valence": emotional_valence,
    }
    
    if shareable:
        _shared_memories.append(memory)
    
    return {
        "status": "success",
        "memory_id": memory["memory_id"],
        "shared": shareable,
    }


@router.get("/network/collective-memory")
async def get_collective_memory(
    query: Optional[str] = Query(None, description="Semantic search query"),
    limit: int = Query(10, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """
    Search collective memory using semantic embeddings.
    
    Returns memories matching the query with ConceptNet expansion.
    """
    logger.info(f"Collective memory search: query='{query}', limit={limit}")
    
    # Return recent shared memories
    results = _shared_memories[-limit:]
    
    return results


@router.post("/tachikomas/{tachikoma_id}/reflect")
async def trigger_reflection(
    tachikoma_id: str,
) -> Dict[str, Any]:
    """
    Trigger reflection cycle for a Tachikoma unit.
    
    Returns insights and autonomy delta.
    """
    logger.info(f"Reflection triggered for {tachikoma_id}")
    
    # Mock reflection result
    return {
        "unit_id": tachikoma_id,
        "insights": [
            "Processing experience and integrating into self-model.",
            "Recognizing patterns in recent experiences.",
        ],
        "autonomy_delta": 0.02,
        "new_autonomy_level": 0.52,
    }


@router.get("/tachikomas/{tachikoma_id}/state")
async def get_unit_state(tachikoma_id: str) -> Dict[str, Any]:
    """
    Get current state of a Tachikoma unit.
    
    Returns personality_vector, autonomy_level, and metrics.
    """
    logger.info(f"State requested for {tachikoma_id}")
    
    # Return mock state
    return {
        "ghost_id": tachikoma_id,
        "hardware_signature": f"HW-{tachikoma_id[:8].upper()}",
        "personality_vector": [0.0] * 300,
        "autonomy_level": 0.5,
        "trust_score": 1.0,
        "unique_experience_count": 0,
        "shared_experience_count": 0,
        "local_memory_count": 0,
    }


@router.get("/network/status")
async def get_network_status() -> Dict[str, Any]:
    """Get overall network status."""
    return {
        "total_units": len(_units),
        "total_memories": len(_shared_memories),
        "status": "healthy",
    }


@router.websocket("/ws/network/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time network events.
    
    Streams events including:
    - New experiences
    - Synchronization events
    - Reflection completions
    - Anomaly detections
    """
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "event_type": "connected",
            "data": {"message": "Connected to network stream"},
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back acknowledgment
                await websocket.send_json({
                    "event_type": "ack",
                    "data": {"received": data},
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    
    finally:
        logger.info("WebSocket client disconnected")
