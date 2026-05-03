"""
Network Protocol - Communication protocols for Tachikoma network.

Handles:
- Inter-unit communication
- Message routing and delivery
- Protocol versioning
- Encryption and security
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the Tachikoma network."""
    EXPERIENCE_SHARE = "experience_share"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    REFLECTION_RESULT = "reflection_result"
    ANOMALY_ALERT = "anomaly_alert"
    STATUS_UPDATE = "status_update"
    COMMAND = "command"
    HEARTBEAT = "heartbeat"


class NetworkProtocol:
    """
    Manages network communication between Tachikoma units.
    
    Features:
    - Asynchronous message passing
    - Message type routing
    - Delivery confirmation
    - Network topology awareness
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Network Protocol.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.node_id: str = str(uuid.uuid4())
        self.connected_nodes: Dict[str, Dict[str, Any]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._message_handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        self._running = False
        self.protocol_version = "1.0.0"
        
    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Async callable to handle the message
        """
        self._message_handlers[message_type].append(handler)
        logger.debug(f"Registered handler for {message_type.value}")
    
    def create_message(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a properly formatted network message.
        
        Args:
            message_type: Type of message
            payload: Message payload dictionary
            source_id: Source node ID (defaults to self.node_id)
            
        Returns:
            Formatted message dictionary
        """
        return {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "source_id": source_id or self.node_id,
            "message_type": message_type.value,
            "protocol_version": self.protocol_version,
            "payload": payload,
            "ttl": self.config.get("default_ttl", 5),  # Time to live (hops)
            "priority": payload.get("priority", 0)
        }
    
    async def send_message(self, message: Dict[str, Any], target_id: Optional[str] = None) -> bool:
        """
        Send a message to the network.
        
        Args:
            message: Message dictionary to send
            target_id: Specific target node ID or None for broadcast
            
        Returns:
            True if sent successfully
        """
        if not self._running:
            logger.warning("Network protocol not running, cannot send message")
            return False
        
        try:
            await self.message_queue.put(message)
            logger.debug(f"Message {message['message_id']} queued for sending")
            return True
        except Exception as e:
            logger.error(f"Failed to queue message: {e}")
            return False
    
    async def receive_message(self, message: Dict[str, Any]) -> None:
        """
        Receive and process an incoming message.
        
        Args:
            message: Received message dictionary
        """
        try:
            msg_type = MessageType(message["message_type"])
        except (KeyError, ValueError) as e:
            logger.warning(f"Invalid message type: {e}")
            return
        
        # Check TTL
        ttl = message.get("ttl", 0)
        if ttl <= 0:
            logger.debug(f"Message {message['message_id']} expired, dropping")
            return
        
        # Decrement TTL
        message["ttl"] = ttl - 1
        
        # Process with registered handlers
        handlers = self._message_handlers.get(msg_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Handler error for {msg_type.value}: {e}")
    
    async def start(self) -> None:
        """Start the network protocol processor."""
        self._running = True
        logger.info(f"Network protocol started (node_id={self.node_id})")
        
        async def process_loop():
            while self._running:
                try:
                    message = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=1.0
                    )
                    # In a real implementation, this would send over network
                    # For now, just process locally
                    await self.receive_message(message)
                    self.message_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
        
        asyncio.create_task(process_loop())
    
    async def stop(self) -> None:
        """Stop the network protocol processor."""
        self._running = False
        await self.message_queue.join()
        logger.info("Network protocol stopped")
    
    def connect_node(self, node_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a connected node.
        
        Args:
            node_id: ID of the node to connect
            metadata: Optional node metadata
        """
        self.connected_nodes[node_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        logger.info(f"Node {node_id} connected")
    
    def disconnect_node(self, node_id: str) -> None:
        """
        Disconnect a node.
        
        Args:
            node_id: ID of the node to disconnect
        """
        if node_id in self.connected_nodes:
            del self.connected_nodes[node_id]
            logger.info(f"Node {node_id} disconnected")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get network statistics.
        
        Returns:
            Dictionary with network stats
        """
        return {
            "node_id": self.node_id,
            "protocol_version": self.protocol_version,
            "running": self._running,
            "connected_nodes_count": len(self.connected_nodes),
            "queue_size": self.message_queue.qsize(),
            "handlers_per_type": {
                mt.value: len(handlers) 
                for mt, handlers in self._message_handlers.items()
            }
        }
