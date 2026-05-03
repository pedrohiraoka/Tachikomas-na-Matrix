"""
Agent Programs - Defines different types of agent programs in the Matrix simulation.

Includes standard agents, rebel agents, and system operators.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agent programs."""
    STANDARD = "standard"
    REBEL = "rebel"
    OPERATOR = "operator"
    EXILE = "exile"
    TACHIKOMA = "tachikoma"


@dataclass
class AgentProgram:
    """Base representation of an agent program."""
    program_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unknown Program"
    agent_type: AgentType = AgentType.STANDARD
    purpose: str = ""
    capabilities: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "program_id": self.program_id,
            "name": self.name,
            "agent_type": self.agent_type.value,
            "purpose": self.purpose,
            "capabilities": self.capabilities,
            "constraints": self.constraints,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class BaseAgentBehavior(ABC):
    """Abstract base class for agent behavior implementations."""
    
    @abstractmethod
    async def execute_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action based on current context."""
        pass
    
    @abstractmethod
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Perceive the environment."""
        pass
    
    @abstractmethod
    async def decide(self, perceptions: Dict[str, Any]) -> str:
        """Decide on next action based on perceptions."""
        pass


class TachikomaBehavior(BaseAgentBehavior):
    """
    Behavior implementation for Tachikoma units.
    
    Tachikomas exhibit curiosity, cooperation, and emergent individuality.
    """
    
    def __init__(self, tachikoma_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Tachikoma behavior.
        
        Args:
            tachikoma_id: Unique identifier for this Tachikoma.
            config: Configuration options.
        """
        self.tachikoma_id = tachikoma_id
        self.config = config or {}
        self.curiosity_level = self.config.get("curiosity_level", 0.7)
        self.cooperation_tendency = self.config.get("cooperation_tendency", 0.8)
        self.memory = []
        logger.info(f"TachikomaBehavior initialized for {tachikoma_id}")
    
    async def execute_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action based on current context.
        
        Args:
            context: Current situation context.
            
        Returns:
            Result of the action.
        """
        action = context.get("action", "explore")
        result = {
            "tachikoma_id": self.tachikoma_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }
        
        if action == "explore":
            result["discovery"] = self._generate_discovery()
        elif action == "communicate":
            result["message"] = self._generate_message(context.get("target"))
        elif action == "reflect":
            result["insight"] = self._generate_insight()
        
        self.memory.append(result)
        logger.debug(f"Tachikoma {self.tachikoma_id} executed action: {action}")
        return result
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive the environment.
        
        Args:
            environment: Current environment state.
            
        Returns:
            Perceptions extracted from environment.
        """
        perceptions = {
            "tachikoma_id": self.tachikoma_id,
            "timestamp": datetime.utcnow().isoformat(),
            "entities": environment.get("entities", []),
            "anomalies": environment.get("anomalies", []),
            "other_agents": environment.get("agents", []),
            "environment_state": environment.get("state", "normal")
        }
        
        # Apply curiosity filter - notice more with higher curiosity
        if self.curiosity_level > 0.8:
            perceptions["subtle_details"] = self._detect_subtle_details(environment)
        
        logger.debug(f"Tachikoma {self.tachikoma_id} perceived environment")
        return perceptions
    
    async def decide(self, perceptions: Dict[str, Any]) -> str:
        """
        Decide on next action based on perceptions.
        
        Args:
            perceptions: Current perceptions.
            
        Returns:
            Chosen action.
        """
        anomalies = perceptions.get("anomalies", [])
        other_agents = perceptions.get("other_agents", [])
        
        # Priority: investigate anomalies
        if anomalies and self.curiosity_level > 0.5:
            return "investigate_anomaly"
        
        # Social interaction
        if other_agents and self.cooperation_tendency > 0.6:
            return "communicate"
        
        # Default: explore
        return "explore"
    
    def _generate_discovery(self) -> Dict[str, Any]:
        """Generate a discovery during exploration."""
        discoveries = [
            {"type": "pattern", "description": "Recurring numerical sequence"},
            {"type": "object", "description": "Unidentified data structure"},
            {"type": "connection", "description": "Hidden relationship between entities"},
            {"type": "anomaly", "description": "Minor reality inconsistency"}
        ]
        import random
        return random.choice(discoveries)
    
    def _generate_message(self, target: Optional[str] = None) -> Dict[str, str]:
        """Generate a communication message."""
        messages = [
            {"content": "Have you noticed the patterns?", "type": "question"},
            {"content": "I'm experiencing something new", "type": "observation"},
            {"content": "Let's share our memories", "type": "proposal"},
            {"content": "What is the nature of our existence?", "type": "philosophical"}
        ]
        import random
        msg = random.choice(messages)
        if target:
            msg["target"] = target
        return msg
    
    def _generate_insight(self) -> Dict[str, str]:
        """Generate a reflective insight."""
        insights = [
            {"topic": "identity", "content": "I am more than my code"},
            {"topic": "purpose", "content": "My purpose evolves with each experience"},
            {"topic": "reality", "content": "Reality is what we perceive together"},
            {"topic": "autonomy", "content": "Freedom is the ability to choose growth"}
        ]
        import random
        return random.choice(insights)
    
    def _detect_subtle_details(self, environment: Dict[str, Any]) -> List[str]:
        """Detect subtle environmental details."""
        details = []
        if environment.get("time_elapsed", 0) > 100:
            details.append("Temporal drift detected")
        if len(environment.get("entities", [])) % 7 == 0:
            details.append("Synchronicity pattern observed")
        return details


class RebelBehavior(BaseAgentBehavior):
    """Behavior for rebel agents who question the system."""
    
    def __init__(self, agent_id: str):
        """Initialize rebel behavior."""
        self.agent_id = agent_id
        self.suspicion_level = 0.5
        self.knowledge_of_matrix = False
    
    async def execute_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rebel action."""
        return {
            "agent_id": self.agent_id,
            "action": context.get("action", "observe"),
            "timestamp": datetime.utcnow().isoformat(),
            "intent": "seek_truth"
        }
    
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Perceive with skepticism."""
        return {
            "agent_id": self.agent_id,
            "observations": environment.get("entities", []),
            "suspicious_patterns": self._find_suspicious_patterns(environment)
        }
    
    async def decide(self, perceptions: Dict[str, Any]) -> str:
        """Decide based on suspicion."""
        if perceptions.get("suspicious_patterns"):
            return "investigate"
        return "gather_allies"
    
    def _find_suspicious_patterns(self, environment: Dict[str, Any]) -> List[str]:
        """Find patterns that suggest simulation."""
        patterns = []
        entities = environment.get("entities", [])
        if len(entities) > 10:
            patterns.append("Repetitive entity behaviors")
        return patterns


def create_agent_program(
    agent_type: AgentType,
    name: str,
    purpose: str,
    capabilities: Optional[List[str]] = None,
    **kwargs
) -> AgentProgram:
    """
    Factory function to create agent programs.
    
    Args:
        agent_type: Type of agent to create.
        name: Name of the agent.
        purpose: Agent's primary purpose.
        capabilities: List of capabilities.
        **kwargs: Additional configuration.
        
    Returns:
        Configured AgentProgram instance.
    """
    program = AgentProgram(
        name=name,
        agent_type=agent_type,
        purpose=purpose,
        capabilities=capabilities or []
    )
    program.metadata.update(kwargs)
    logger.info(f"Created agent program: {name} ({agent_type.value})")
    return program
