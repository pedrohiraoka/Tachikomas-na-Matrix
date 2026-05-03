"""
Memory Synchronization - Handles synchronization of memories across Tachikoma network.

Implements Redis Pub/Sub for experience sharing, conflict resolution via trust scores,
and distributed fine-tuning for collective memory updates.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import numpy as np

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from .tachikoma_unit import TachikomaUnit

logger = logging.getLogger(__name__)


class MemorySync:
    """
    Manages synchronization of memories across the Tachikoma network.
    
    Features:
    - Redis Pub/Sub for real-time experience propagation
    - Trust score-based conflict resolution
    - Distributed fine-tuning for collective memory updates
    - Anomaly quarantine for suspicious memories
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", config: Optional[Dict[str, Any]] = None):
        """
        Initialize Memory Synchronization system.
        
        Args:
            redis_url: Redis connection URL
            config: Configuration dictionary
        """
        self.redis_url = redis_url
        self.config = config or {}
        self.redis: Optional['aioredis.Redis'] = None
        self.pubsub: Optional['aioredis.client.PubSub'] = None
        self.units: Dict[str, TachikomaUnit] = {}
        self.shared_memory_pool: List[Dict[str, Any]] = []
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None
        self._message_handlers: List[Callable] = []
        
    async def connect(self) -> None:
        """Establish connection to Redis."""
        if aioredis is None:
            logger.warning("Redis not available, running in mock mode")
            return
        
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("tachikoma:experiences")
            self._running = True
            logger.info("Connected to Redis for memory synchronization")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Running in offline mode without synchronization")
    
    async def disconnect(self) -> None:
        """Disconnect from Redis and cleanup."""
        self._running = False
        
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Disconnected from memory synchronization")
    
    def register_unit(self, unit: TachikomaUnit) -> None:
        """
        Register a Tachikoma unit for synchronization.
        
        Args:
            unit: TachikomaUnit to register
        """
        self.units[unit.ghost_id] = unit
        logger.info(f"Registered unit {unit.ghost_id} for synchronization")
    
    def unregister_unit(self, ghost_id: str) -> None:
        """
        Unregister a Tachikoma unit from synchronization.
        
        Args:
            ghost_id: UUID of unit to unregister
        """
        if ghost_id in self.units:
            del self.units[ghost_id]
            logger.info(f"Unregistered unit {ghost_id} from synchronization")
    
    async def share_experience(self, unit: TachikomaUnit, experience: Dict[str, Any]) -> bool:
        """
        Share an experience from a unit to the collective memory pool.
        
        Args:
            unit: TachikomaUnit sharing the experience
            experience: Experience dictionary to share
            
        Returns:
            True if successfully shared, False otherwise
        """
        if unit.is_isolated:
            logger.debug(f"Unit {unit.ghost_id} is isolated, cannot share experiences")
            return False
        
        if not experience.get("shareable", True):
            return False
        
        # Check autonomy threshold for consent
        autonomy_threshold = self.config.get("require_consent_above_autonomy", 0.8)
        if unit.autonomy_level > autonomy_threshold:
            # High autonomy units can choose not to share
            logger.debug(f"Unit {unit.ghost_id} has high autonomy, sharing is optional")
        
        # Prepare experience for sharing
        shared_experience = {
            "memory_id": experience.get("memory_id", ""),
            "ghost_id": unit.ghost_id,
            "content": experience.get("content", ""),
            "embedding": experience.get("embedding", []).tolist() if isinstance(experience.get("embedding"), np.ndarray) else experience.get("embedding", []),
            "conceptnet_concepts": experience.get("conceptnet_concepts", []),
            "timestamp": datetime.utcnow().isoformat(),
            "trust_score": unit.trust_score,
            "emotional_valence": experience.get("emotional_valence", 0.0),
            "metadata": experience.get("metadata", {})
        }
        
        # Publish to Redis
        if self.redis and self._running:
            try:
                await self.redis.publish(
                    "tachikoma:experiences",
                    json.dumps(shared_experience, default=str)
                )
                logger.debug(f"Shared experience {shared_experience['memory_id']} to network")
            except Exception as e:
                logger.error(f"Failed to publish experience: {e}")
        
        # Add to local shared memory pool
        self.shared_memory_pool.append(shared_experience)
        
        # Limit pool size
        max_pool_size = self.config.get("max_shared_memory_pool_size", 10000)
        if len(self.shared_memory_pool) > max_pool_size:
            self.shared_memory_pool = self.shared_memory_pool[-max_pool_size:]
        
        return True
    
    async def receive_experience(self, experience: Dict[str, Any]) -> Optional[str]:
        """
        Receive an experience from the network and integrate it.
        
        Args:
            experience: Experience dictionary received from network
            
        Returns:
            memory_id if integrated successfully, None otherwise
        """
        source_ghost_id = experience.get("ghost_id")
        
        # Check if from isolated unit
        if source_ghost_id and source_ghost_id in self.units:
            source_unit = self.units[source_ghost_id]
            if source_unit.is_isolated:
                logger.warning(f"Received experience from isolated unit {source_ghost_id}, quarantining")
                return None
        
        # Check trust score
        trust_score = experience.get("trust_score", 0.5)
        min_trust = self.config.get("min_trust_for_sync", 0.3)
        
        if trust_score < min_trust:
            logger.warning(f"Experience from low-trust source ({trust_score}), rejecting")
            return None
        
        # Anomaly detection
        if self.config.get("anomaly_quarantine_enabled", True):
            if self._detect_anomaly(experience):
                logger.warning(f"Potential anomaly detected in experience, quarantining")
                return None
        
        # Integrate into shared memory pool
        memory_id = experience.get("memory_id")
        self.shared_memory_pool.append(experience)
        
        logger.debug(f"Integrated experience {memory_id} from {source_ghost_id}")
        return memory_id
    
    def _detect_anomaly(self, experience: Dict[str, Any]) -> bool:
        """
        Detect potential anomalies in an experience.
        
        Args:
            experience: Experience dictionary to analyze
            
        Returns:
            True if anomaly detected, False otherwise
        """
        # Simple anomaly detection based on emotional valence extremes
        valence = experience.get("emotional_valence", 0.0)
        if abs(valence) > 0.95:
            return True
        
        # Check for unusual concept combinations
        concepts = experience.get("conceptnet_concepts", [])
        if len(concepts) > 50:  # Unusually high number of concepts
            return True
        
        return False
    
    async def start_sync_listener(self) -> None:
        """Start listening for incoming experiences from the network."""
        if not self.redis or not self._running:
            logger.warning("Cannot start sync listener: Redis not connected")
            return
        
        async def listen_loop():
            while self._running:
                try:
                    message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message["type"] == "message":
                        data = json.loads(message["data"])
                        await self.receive_experience(data)
                        
                        # Call registered handlers
                        for handler in self._message_handlers:
                            try:
                                await handler(data)
                            except Exception as e:
                                logger.error(f"Message handler error: {e}")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Sync listener error: {e}")
                    await asyncio.sleep(1)
        
        self._sync_task = asyncio.create_task(listen_loop())
        logger.info("Started memory synchronization listener")
    
    def add_message_handler(self, handler: Callable) -> None:
        """
        Add a handler for incoming experience messages.
        
        Args:
            handler: Async callable that takes experience dict as argument
        """
        self._message_handlers.append(handler)
        logger.debug(f"Added message handler: {handler.__name__}")
    
    async def query_collective_memory(
        self, 
        query_embedding: np.ndarray, 
        limit: int = 10,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Query the collective memory pool using semantic similarity.
        
        Args:
            query_embedding: Embedding vector for the query
            limit: Maximum number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of matching experiences with similarity scores
        """
        if not self.shared_memory_pool:
            return []
        
        # Normalize query embedding
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        results = []
        for experience in self.shared_memory_pool:
            emb = experience.get("embedding", [])
            if isinstance(emb, list) and len(emb) > 0:
                exp_emb = np.array(emb)
                exp_norm = exp_emb / (np.linalg.norm(exp_emb) + 1e-8)
                similarity = float(np.dot(query_norm, exp_norm))
                
                if similarity >= min_similarity:
                    results.append({
                        **experience,
                        "similarity": similarity
                    })
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """
        Get synchronization statistics.
        
        Returns:
            Dictionary with sync statistics
        """
        return {
            "connected": self.redis is not None and self._running,
            "units_registered": len(self.units),
            "shared_memory_pool_size": len(self.shared_memory_pool),
            "message_handlers": len(self._message_handlers),
            "config": self.config
        }
