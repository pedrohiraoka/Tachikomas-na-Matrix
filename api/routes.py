"""FastAPI routes for Tachikoma Matrix API."""
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .models import ExperienceInput, MemoryResponse, TachikomaState, ReflectionResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["tachikoma"])

# In-memory storage (replace with DB in production)
tachikomas: Dict[str, dict] = {}
memories: Dict[str, List[dict]] = {}
reflection_results: Dict[str, List[dict]] = {}


@router.post("/tachikomas/{tachikoma_id}/experience", response_model=Dict)
async def register_experience(tachikoma_id: str, experience: ExperienceInput):
    """Register a new experience for a Tachikoma unit."""
    logger.info(f"Registering experience for {tachikoma_id}")
    
    if tachikoma_id not in tachikomas:
        tachikomas[tachikoma_id] = {
            "ghost_id": tachikoma_id,
            "autonomy_level": 0.5,
            "trust_score": 0.8,
            "experiences": [],
            "personality_vector": [0.0] * 300
        }
    
    memory_entry = {
        "memory_id": f"mem_{tachikoma_id}_{len(memories.get(tachikoma_id, []))}",
        "content": experience.content,
        "shareable": experience.shareable,
        "metadata": experience.metadata,
        "concepts": [],
        "valence": 0.0
    }
    
    if tachikoma_id not in memories:
        memories[tachikoma_id] = []
    memories[tachikoma_id].append(memory_entry)
    tachikomas[tachikoma_id]["experiences"].append(memory_entry)
    
    return {"status": "success", "memory_id": memory_entry["memory_id"]}


@router.get("/network/collective-memory", response_model=List[MemoryResponse])
async def search_collective_memory(query: str, limit: int = 10):
    """Search collective memory using semantic query."""
    logger.info(f"Searching collective memory for: {query}")
    
    results = []
    for tid, mems in memories.items():
        for mem in mems:
            if query.lower() in mem.get("content", "").lower():
                results.append(MemoryResponse(
                    memory_id=mem["memory_id"],
                    content=mem["content"],
                    concepts=mem.get("concepts", []),
                    valence=mem.get("valence", 0.0),
                    timestamp="2024-01-01T00:00:00",
                    score=0.8
                ))
                if len(results) >= limit:
                    return results
    
    return results


@router.post("/tachikomas/{tachikoma_id}/reflect", response_model=ReflectionResult)
async def trigger_reflection(tachikoma_id: str):
    """Trigger reflection cycle for a Tachikoma unit."""
    logger.info(f"Triggering reflection for {tachikoma_id}")
    
    if tachikoma_id not in tachikomas:
        raise HTTPException(status_code=404, detail="Tachikoma not found")
    
    # Simulate reflection
    insights = [{
        "question": "What distinguishes my consciousness from others?",
        "insight": "Individuality arises from unique combinations of shared knowledge.",
        "confidence": 0.85,
        "based_on_memories": 3
    }]
    
    autonomy_delta = 0.05
    tachikomas[tachikoma_id]["autonomy_level"] = min(
        1.0, tachikomas[tachikoma_id]["autonomy_level"] + autonomy_delta
    )
    
    result = ReflectionResult(
        tachikoma_id=tachikoma_id,
        timestamp="2024-01-01T00:00:00",
        questions_generated=1,
        insights=insights,
        autonomy_delta=autonomy_delta,
        reflection_depth=1
    )
    
    if tachikoma_id not in reflection_results:
        reflection_results[tachikoma_id] = []
    reflection_results[tachikoma_id].append(result.dict())
    
    return result


@router.get("/tachikomas/{tachikoma_id}/state", response_model=TachikomaState)
async def get_tachikoma_state(tachikoma_id: str):
    """Get current state of a Tachikoma unit."""
    if tachikoma_id not in tachikomas:
        raise HTTPException(status_code=404, detail="Tachikoma not found")
    
    t = tachikomas[tachikoma_id]
    exps = t.get("experiences", [])
    
    return TachikomaState(
        ghost_id=t["ghost_id"],
        personality_vector=t["personality_vector"][:10],  # First 10 dims
        autonomy_level=t["autonomy_level"],
        trust_score=t["trust_score"],
        unique_experience_count=len(exps),
        shared_experience_count=sum(1 for e in exps if e.get("shareable", False)),
        last_sync_timestamp="2024-01-01T00:00:00"
    )


@router.websocket("/ws/network/realtime")
async def websocket_network_realtime(websocket: WebSocket):
    """WebSocket endpoint for real-time network events."""
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Send periodic updates
            await websocket.send_json({
                "type": "network_update",
                "unit_count": len(tachikomas),
                "total_memories": sum(len(m) for m in memories.values()),
                "timestamp": "2024-01-01T00:00:00"
            })
            
            # Check for incoming messages
            try:
                data = await websocket.receive_text()
                logger.info(f"Received: {data}")
            except:
                pass
            
            import asyncio
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
