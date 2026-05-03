"""
Memory Sync Protocol - Protocolo de sincronização de memórias via Redis Pub/Sub.

Este módulo implementa o mecanismo de sincronização de experiências entre unidades
Tachikoma, permitindo a formação de memória coletiva enquanto preserva individualidade.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import numpy as np

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from .tachikoma_unit import TachikomaUnit, MemoryEntry

logger = logging.getLogger(__name__)


class SharedMemoryPool:
    """
    Pool de memória compartilhada da rede Tachikoma.
    
    Armazena memórias compartilhadas por todas as unidades e permite
    busca semântica e recuperação distribuída.
    """
    
    def __init__(self, max_size: int = 10000) -> None:
        """
        Inicializa o pool de memória compartilhada.
        
        Args:
            max_size: Número máximo de memórias no pool
        """
        self.memories: List[Dict[str, Any]] = []
        self.max_size = max_size
        self._lock = asyncio.Lock()
        logger.info(f"SharedMemoryPool initialized (max_size={max_size})")
    
    async def add_memory(
        self,
        memory_data: Dict[str, Any],
        source_unit_id: str,
    ) -> bool:
        """
        Adiciona uma memória ao pool compartilhado.
        
        Args:
            memory_data: Dados da memória
            source_unit_id: ID da unidade de origem
            
        Returns:
            bool: True se adicionado com sucesso
        """
        async with self._lock:
            memory_entry = {
                "memory_id": memory_data.get("memory_id", str(datetime.utcnow().timestamp())),
                "content": memory_data.get("content", ""),
                "embedding": memory_data.get("embedding", []),
                "conceptnet_concepts": memory_data.get("conceptnet_concepts", []),
                "timestamp": memory_data.get("timestamp", datetime.utcnow().isoformat()),
                "source_unit_id": source_unit_id,
                "trust_score": memory_data.get("trust_score", 1.0),
                "integration_count": 0,
            }
            
            self.memories.append(memory_entry)
            
            # Manter tamanho máximo
            if len(self.memories) > self.max_size:
                self.memories = self.memories[-self.max_size:]
            
            logger.debug(f"Added memory to pool from {source_unit_id[:8]}...")
            return True
    
    async def search_by_similarity(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Busca memórias por similaridade semântica.
        
        Args:
            query_embedding: Vetor de embedding da consulta
            limit: Número máximo de resultados
            threshold: Limiar mínimo de similaridade
            
        Returns:
            Lista de memórias ordenadas por similaridade
        """
        if not self.memories:
            return []
        
        results = []
        
        for memory in self.memories:
            mem_embedding = np.array(memory.get("embedding", []))
            if len(mem_embedding) == 0:
                continue
            
            # Calcular similaridade coseno
            norm_query = np.linalg.norm(query_embedding)
            norm_mem = np.linalg.norm(mem_embedding)
            
            if norm_query < 1e-8 or norm_mem < 1e-8:
                continue
            
            similarity = np.dot(query_embedding, mem_embedding) / (norm_query * norm_mem)
            similarity = float((similarity + 1) / 2)  # Normalizar para 0-1
            
            if similarity >= threshold:
                result = memory.copy()
                result["similarity"] = similarity
                results.append(result)
        
        # Ordenar por similaridade
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:limit]
    
    async def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna as memórias mais recentes do pool.
        
        Args:
            limit: Número máximo de memórias
            
        Returns:
            Lista de memórias recentes
        """
        return self.memories[-limit:]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do pool."""
        return {
            "total_memories": len(self.memories),
            "max_size": self.max_size,
            "utilization": len(self.memories) / self.max_size if self.max_size > 0 else 0,
        }


class MemorySyncProtocol:
    """
    Protocolo de sincronização de memórias via Redis Pub/Sub.
    
    Implementa:
    - Publicação de experiências shareable
    - Assinatura de canais de sincronização
    - Resolução de conflitos via trust score
    - Propagação seletiva baseada em autonomia
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        channel_prefix: str = "tachikoma_sync",
    ) -> None:
        """
        Inicializa o protocolo de sincronização.
        
        Args:
            redis_url: URL de conexão Redis
            channel_prefix: Prefixo para canais Pub/Sub
        """
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix
        self.pubsub = None
        self.redis_client = None
        self.subscribed_channels: set = set()
        self.shared_pool: Optional[SharedMemoryPool] = None
        self._running = False
        self._message_handlers: List[Callable] = []
        
        logger.info(f"MemorySyncProtocol initialized (prefix={channel_prefix})")
    
    async def connect(self) -> bool:
        """
        Estabelece conexão com Redis.
        
        Returns:
            bool: True se conectado com sucesso
        """
        if aioredis is None:
            logger.warning("Redis client not available, running in mock mode")
            return False
        
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            self.pubsub = self.redis_client.pubsub()
            self._running = True
            logger.info(f"Connected to Redis: {self.redis_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Desconecta do Redis e limpa recursos."""
        self._running = False
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Disconnected from Redis")
    
    def set_shared_pool(self, pool: SharedMemoryPool) -> None:
        """Define o pool de memória compartilhada."""
        self.shared_pool = pool
        logger.info("Shared memory pool attached")
    
    async def publish_experience(
        self,
        unit: TachikomaUnit,
        memory: MemoryEntry,
    ) -> bool:
        """
        Publica uma experiência para sincronização na rede.
        
        Args:
            unit: Unidade publicando
            memory: Memória sendo compartilhada
            
        Returns:
            bool: True se publicado com sucesso
        """
        if not memory.shareable:
            logger.debug(f"Memory not shareable: {memory.memory_id}")
            return False
        
        message = {
            "type": "experience_share",
            "source_unit_id": unit.ghost_id,
            "trust_score": unit.trust_score,
            "autonomy_level": unit.autonomy_level,
            "memory": {
                "memory_id": memory.memory_id,
                "content": memory.content,
                "embedding": memory.embedding.tolist(),
                "conceptnet_concepts": memory.conceptnet_concepts,
                "timestamp": memory.timestamp.isoformat(),
                "emotional_valence": memory.emotional_valence,
            },
            "published_at": datetime.utcnow().isoformat(),
        }
        
        channel = f"{self.channel_prefix}:experiences"
        
        if self.redis_client and self._running:
            try:
                await self.redis_client.publish(channel, json.dumps(message))
                logger.debug(f"Published experience to {channel}")
                return True
            except Exception as e:
                logger.error(f"Failed to publish experience: {e}")
                return False
        else:
            # Mock mode - apenas log
            logger.debug(f"[MOCK] Published experience: {message['memory']['memory_id'][:8]}...")
            
            # Notificar handlers locais
            await self._notify_local_handlers(message)
            return True
    
    async def subscribe_to_channel(self, channel: str) -> bool:
        """
        Inscreve-se em um canal de sincronização.
        
        Args:
            channel: Nome do canal
            
        Returns:
            bool: True se inscrito com sucesso
        """
        full_channel = f"{self.channel_prefix}:{channel}"
        
        if full_channel in self.subscribed_channels:
            return True
        
        if self.pubsub:
            try:
                await self.pubsub.subscribe(full_channel)
                self.subscribed_channels.add(full_channel)
                logger.info(f"Subscribed to channel: {full_channel}")
                return True
            except Exception as e:
                logger.error(f"Failed to subscribe to {full_channel}: {e}")
                return False
        else:
            self.subscribed_channels.add(full_channel)
            logger.info(f"[MOCK] Subscribed to channel: {full_channel}")
            return True
    
    async def listen_for_updates(
        self,
        handler: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Escuta atualizações de sincronização em background.
        
        Args:
            handler: Função callback para processar mensagens
        """
        if handler:
            self._message_handlers.append(handler)
        
        if not self.pubsub:
            logger.debug("Running in mock mode, no Redis listener")
            return
        
        try:
            while self._running:
                message = await self.pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                
                if message and message["type"] == "message":
                    await self._process_message(message["data"])
        except Exception as e:
            logger.error(f"Error listening for updates: {e}")
    
    async def _process_message(self, data: str) -> None:
        """Processa uma mensagem recebida."""
        try:
            message = json.loads(data)
            await self._notify_local_handlers(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _notify_local_handlers(self, message: Dict[str, Any]) -> None:
        """Notifica todos os handlers registrados."""
        for handler in self._message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    async def resolve_conflict(
        self,
        memory_a: Dict[str, Any],
        memory_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Resolve conflito entre duas memórias usando trust score.
        
        Args:
            memory_a: Primeira memória
            memory_b: Segunda memória
            
        Returns:
            Memória vencedora
        """
        trust_a = memory_a.get("trust_score", 1.0)
        trust_b = memory_b.get("trust_score", 1.0)
        
        if trust_a >= trust_b:
            logger.debug(f"Conflict resolved: memory A wins (trust={trust_a:.2f})")
            return memory_a
        else:
            logger.debug(f"Conflict resolved: memory B wins (trust={trust_b:.2f})")
            return memory_b
    
    async def sync_unit_with_pool(
        self,
        unit: TachikomaUnit,
        download_limit: int = 10,
    ) -> int:
        """
        Sincroniza uma unidade com o pool compartilhado.
        
        Args:
            unit: Unidade para sincronizar
            download_limit: Número máximo de memórias para baixar
            
        Returns:
            int: Número de memórias sincronizadas
        """
        if not self.shared_pool:
            logger.warning("No shared pool available")
            return 0
        
        synced_count = 0
        
        # Obter memórias recentes do pool
        recent_memories = await self.shared_pool.get_recent(download_limit)
        
        for mem_data in recent_memories:
            # Verificar se unidade já tem esta memória
            existing_ids = {m.memory_id for m in unit.local_memory}
            
            if mem_data["memory_id"] not in existing_ids:
                # Criar embedding numpy
                embedding = np.array(mem_data.get("embedding", []))
                
                # Armazenar na unidade
                await unit.store_experience(
                    content=f"[SHARED] {mem_data['content']}",
                    embedding=embedding,
                    shareable=False,
                    metadata={
                        "source_unit_id": mem_data.get("source_unit_id"),
                        "shared": True,
                    },
                )
                synced_count += 1
        
        # Atualizar timestamp de sincronização
        await unit.sync_with_pool(self.shared_pool)
        
        logger.info(
            f"Synced {synced_count} memories for {unit.ghost_id[:8]}..."
        )
        
        return synced_count
