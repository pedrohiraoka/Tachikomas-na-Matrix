"""
Network Protocol - Protocolo de comunicação da rede Tachikoma.

Este módulo implementa os protocolos de comunicação entre unidades,
incluindo descoberta, handshake e troca de mensagens.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class NetworkMessage:
    """Representa uma mensagem na rede Tachikoma."""
    
    def __init__(
        self,
        msg_type: str,
        sender_id: str,
        payload: Dict[str, Any],
        recipient_id: Optional[str] = None,
    ) -> None:
        """
        Inicializa uma mensagem de rede.
        
        Args:
            msg_type: Tipo da mensagem
            sender_id: ID do remetente
            payload: Conteúdo da mensagem
            recipient_id: ID do destinatário (None para broadcast)
        """
        self.message_id = str(uuid.uuid4())
        self.msg_type = msg_type
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.payload = payload
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável."""
        return {
            "message_id": self.message_id,
            "type": self.msg_type,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkMessage':
        """Cria mensagem a partir de dicionário."""
        msg = cls(
            msg_type=data["type"],
            sender_id=data["sender_id"],
            payload=data["payload"],
            recipient_id=data.get("recipient_id"),
        )
        msg.message_id = data["message_id"]
        msg.timestamp = datetime.fromisoformat(data["timestamp"])
        return msg
    
    def __repr__(self) -> str:
        return f"NetworkMessage(type={self.msg_type}, from={self.sender_id[:8]}...)"


class NetworkProtocol:
    """
    Protocolo de comunicação da rede Tachikoma.
    
    Implementa:
    - Descoberta de unidades na rede
    - Handshake inicial entre unidades
    - Troca de mensagens ponto-a-ponto e broadcast
    - Manutenção de estado de conexão
    """
    
    # Tipos de mensagem
    MSG_DISCOVER = "discover"
    MSG_HANDSHAKE = "handshake"
    MSG_HEARTBEAT = "heartbeat"
    MSG_EXPERIENCE = "experience"
    MSG_QUERY = "query"
    MSG_RESPONSE = "response"
    
    def __init__(self, node_id: str) -> None:
        """
        Inicializa o protocolo de rede.
        
        Args:
            node_id: ID único deste nó na rede
        """
        self.node_id = node_id
        self.connected_peers: Dict[str, Dict[str, Any]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._message_handlers: Dict[str, List[Callable]] = {}
        logger.info(f"NetworkProtocol initialized for node {node_id[:8]}...")
    
    async def start(self) -> None:
        """Inicia o protocolo de rede."""
        self._running = True
        logger.info("Network protocol started")
    
    async def stop(self) -> None:
        """Para o protocolo de rede."""
        self._running = False
        
        # Notificar peers
        for peer_id in list(self.connected_peers.keys()):
            await self.send_message(
                NetworkMessage(
                    msg_type=self.MSG_HEARTBEAT,
                    sender_id=self.node_id,
                    payload={"status": "disconnecting"},
                    recipient_id=peer_id,
                )
            )
        
        self.connected_peers.clear()
        logger.info("Network protocol stopped")
    
    def register_handler(
        self,
        msg_type: str,
        handler: Callable[[NetworkMessage], Any],
    ) -> None:
        """
        Registra um handler para um tipo de mensagem.
        
        Args:
            msg_type: Tipo de mensagem para handler
            handler: Função callback para processar mensagens
        """
        if msg_type not in self._message_handlers:
            self._message_handlers[msg_type] = []
        self._message_handlers[msg_type].append(handler)
        logger.debug(f"Registered handler for message type: {msg_type}")
    
    async def send_message(self, message: NetworkMessage) -> bool:
        """
        Envia uma mensagem na rede.
        
        Args:
            message: Mensagem a ser enviada
            
        Returns:
            bool: True se enviado com sucesso
        """
        if not self._running:
            logger.warning("Network protocol not running")
            return False
        
        try:
            # Se tem destinatário específico, enviar apenas para ele
            if message.recipient_id:
                if message.recipient_id in self.connected_peers:
                    await self._deliver_to_peer(message.recipient_id, message)
                    return True
                else:
                    logger.warning(f"Peer {message.recipient_id[:8]}... not connected")
                    return False
            else:
                # Broadcast para todos os peers
                await self._broadcast(message)
                return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def _deliver_to_peer(
        self,
        peer_id: str,
        message: NetworkMessage,
    ) -> None:
        """Entrega mensagem para um peer específico."""
        # Em implementação real, enviaria via socket/Redis
        # Aqui apenas coloca na fila de processamento
        await self.message_queue.put(message.to_dict())
        logger.debug(f"Delivered message to {peer_id[:8]}...")
    
    async def _broadcast(self, message: NetworkMessage) -> None:
        """Broadcast para todos os peers conectados."""
        for peer_id in self.connected_peers.keys():
            if peer_id != message.sender_id:
                await self._deliver_to_peer(peer_id, message)
        logger.debug(f"Broadcast message from {message.sender_id[:8]}...")
    
    async def receive_message(self, timeout: float = 1.0) -> Optional[NetworkMessage]:
        """
        Recebe uma mensagem da rede.
        
        Args:
            timeout: Tempo máximo de espera em segundos
            
        Returns:
            NetworkMessage ou None se timeout
        """
        try:
            data = await asyncio.wait_for(
                self.message_queue.get(),
                timeout=timeout,
            )
            message = NetworkMessage.from_dict(data)
            await self._process_message(message)
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None
    
    async def _process_message(self, message: NetworkMessage) -> None:
        """Processa uma mensagem recebida."""
        handlers = self._message_handlers.get(message.msg_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    async def discover_peers(self) -> List[str]:
        """
        Descobre peers na rede.
        
        Returns:
            Lista de IDs de peers descobertos
        """
        discover_msg = NetworkMessage(
            msg_type=self.MSG_DISCOVER,
            sender_id=self.node_id,
            payload={"action": "discover"},
        )
        
        await self._broadcast(discover_msg)
        
        # Em implementação real, aguardaria respostas
        # Aqui retorna peers já conhecidos
        return list(self.connected_peers.keys())
    
    async def handshake(self, peer_id: str) -> bool:
        """
        Realiza handshake com um peer.
        
        Args:
            peer_id: ID do peer para handshake
            
        Returns:
            bool: True se handshake bem-sucedido
        """
        handshake_msg = NetworkMessage(
            msg_type=self.MSG_HANDSHAKE,
            sender_id=self.node_id,
            payload={
                "protocol_version": "1.0",
                "capabilities": ["experience_share", "memory_sync", "reflection"],
            },
            recipient_id=peer_id,
        )
        
        success = await self.send_message(handshake_msg)
        
        if success:
            self.connected_peers[peer_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "last_heartbeat": datetime.utcnow().isoformat(),
                "protocol_version": "1.0",
            }
            logger.info(f"Handshake completed with {peer_id[:8]}...")
        
        return success
    
    async def send_heartbeat(self) -> None:
        """Envia heartbeat para todos os peers."""
        heartbeat_msg = NetworkMessage(
            msg_type=self.MSG_HEARTBEAT,
            sender_id=self.node_id,
            payload={
                "timestamp": datetime.utcnow().isoformat(),
                "status": "active",
            },
        )
        
        await self._broadcast(heartbeat_msg)
        
        # Atualizar último heartbeat de todos os peers
        for peer_id in self.connected_peers:
            self.connected_peers[peer_id]["last_heartbeat"] = datetime.utcnow().isoformat()
    
    async def share_experience(
        self,
        experience_data: Dict[str, Any],
        target_peers: Optional[List[str]] = None,
    ) -> int:
        """
        Compartilha uma experiência com peers.
        
        Args:
            experience_data: Dados da experiência
            target_peers: Lista de peers alvo (None para broadcast)
            
        Returns:
            int: Número de peers que receberam a experiência
        """
        sent_count = 0
        
        if target_peers:
            for peer_id in target_peers:
                msg = NetworkMessage(
                    msg_type=self.MSG_EXPERIENCE,
                    sender_id=self.node_id,
                    payload=experience_data,
                    recipient_id=peer_id,
                )
                if await self.send_message(msg):
                    sent_count += 1
        else:
            msg = NetworkMessage(
                msg_type=self.MSG_EXPERIENCE,
                sender_id=self.node_id,
                payload=experience_data,
            )
            await self._broadcast(msg)
            sent_count = len(self.connected_peers)
        
        logger.info(f"Shared experience with {sent_count} peers")
        return sent_count
    
    def get_network_status(self) -> Dict[str, Any]:
        """Retorna status atual da rede."""
        return {
            "node_id": self.node_id,
            "running": self._running,
            "connected_peers": len(self.connected_peers),
            "peers": list(self.connected_peers.keys()),
            "queue_size": self.message_queue.qsize(),
        }
