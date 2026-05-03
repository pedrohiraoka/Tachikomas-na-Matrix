"""
Human Pod Interface - Simulates interface with human operators outside the Matrix.

Provides communication channels between simulation and external controllers.
"""

import logging
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import uuid
import json

logger = logging.getLogger(__name__)


@dataclass
class OperatorCommand:
    """Represents a command from a human operator."""
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operator_id: str = ""
    command_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    executed: bool = False
    result: Optional[Dict[str, Any]] = None


class HumanPodInterface:
    """
    Interface for human operators to interact with the simulation.
    
    Supports command injection, monitoring, and emergency controls.
    """
    
    def __init__(self):
        self.command_queue: asyncio.Queue = asyncio.Queue()
        self.connected_operators: Dict[str, Dict[str, Any]] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self.audit_log: List[Dict[str, Any]] = []
        logger.info("HumanPodInterface initialized")
    
    def register_operator(
        self, 
        operator_id: str, 
        credentials: Dict[str, Any],
        permissions: List[str]
    ) -> bool:
        """Register a human operator."""
        self.connected_operators[operator_id] = {
            "credentials": credentials,
            "permissions": permissions,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        logger.info(f"Operator registered: {operator_id}")
        return True
    
    def register_command_handler(
        self, 
        command_type: str, 
        handler: Callable
    ) -> None:
        """Register a handler for a command type."""
        self.command_handlers[command_type] = handler
        logger.debug(f"Command handler registered: {command_type}")
    
    async def submit_command(
        self, 
        operator_id: str, 
        command_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit a command from an operator."""
        if operator_id not in self.connected_operators:
            raise ValueError(f"Operator {operator_id} not connected")
        
        operator = self.connected_operators[operator_id]
        if command_type not in operator["permissions"]:
            raise PermissionError(f"Operator lacks permission for {command_type}")
        
        command = OperatorCommand(
            operator_id=operator_id,
            command_type=command_type,
            parameters=parameters or {}
        )
        
        await self.command_queue.put(command)
        self._log_command(command, "submitted")
        logger.info(f"Command submitted by {operator_id}: {command_type}")
        return command.command_id
    
    async def process_commands(self) -> None:
        """Process commands from the queue."""
        while True:
            try:
                command = await asyncio.wait_for(
                    self.command_queue.get(), 
                    timeout=1.0
                )
                
                handler = self.command_handlers.get(command.command_type)
                if handler:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(command.parameters)
                        else:
                            result = handler(command.parameters)
                        command.result = result
                        command.executed = True
                        self._log_command(command, "executed")
                    except Exception as e:
                        command.result = {"error": str(e)}
                        self._log_command(command, "failed")
                
                self.command_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def _log_command(self, command: OperatorCommand, status: str) -> None:
        """Log command for audit trail."""
        self.audit_log.append({
            "command_id": command.command_id,
            "operator_id": command.operator_id,
            "command_type": command.command_type,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:]
    
    def disconnect_operator(self, operator_id: str) -> None:
        """Disconnect an operator."""
        if operator_id in self.connected_operators:
            del self.connected_operators[operator_id]
            logger.info(f"Operator disconnected: {operator_id}")
