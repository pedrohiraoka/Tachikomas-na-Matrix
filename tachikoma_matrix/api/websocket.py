"""
WebSocket Manager - Gerenciador de conexões WebSocket.
"""

import logging
from typing import Dict, List, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Gerenciador de conexões WebSocket."""
    
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected ({len(self.active_connections)} active)")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected ({len(self.active_connections)} active)")
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connections."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
    
    async def send_to_client(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
