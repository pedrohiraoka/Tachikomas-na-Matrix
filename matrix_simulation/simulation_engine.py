"""
Simulation Engine - Core event-based simulation loop for the Matrix environment.

Provides asynchronous event processing, procedural scenario generation,
and reality rule management.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import random

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the simulation."""
    SCENARIO_CHANGE = "scenario_change"
    ANOMALY_DETECTED = "anomaly_detected"
    AGENT_ACTION = "agent_action"
    REALITY_SHIFT = "reality_shift"
    SYSTEM_COMMAND = "system_command"
    MEMORY_SYNC = "memory_sync"
    REFLECTION_TRIGGER = "reflection_trigger"


@dataclass
class SimulationEvent:
    """Represents an event in the simulation."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.AGENT_ACTION
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "target": self.target,
            "data": self.data,
            "priority": self.priority
        }


@dataclass
class RealityRule:
    """Defines a rule governing the simulated reality."""
    rule_id: str
    name: str
    description: str
    condition: Callable[[Dict[str, Any]], bool]
    effect: Callable[[Dict[str, Any]], Dict[str, Any]]
    active: bool = True
    priority: int = 0


@dataclass
class Scenario:
    """A procedural scenario in the simulation."""
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Scenario"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    active_agents: Set[str] = field(default_factory=set)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class SimulationEngine:
    """
    Main simulation engine managing the Matrix-like environment.
    
    Handles event processing, scenario generation, and reality rule enforcement.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the simulation engine.
        
        Args:
            config: Configuration dictionary for simulation parameters.
        """
        self.config = config or {}
        self.events: asyncio.Queue = asyncio.Queue()
        self.reality_rules: Dict[str, RealityRule] = {}
        self.scenarios: Dict[str, Scenario] = {}
        self.active_scenario: Optional[Scenario] = None
        self.agents: Dict[str, Any] = {}
        self.anomalies: List[Dict[str, Any]] = []
        self.running = False
        self.event_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self._task: Optional[asyncio.Task] = None
        
        logger.info("SimulationEngine initialized")
    
    def register_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> None:
        """
        Register an agent in the simulation.
        
        Args:
            agent_id: Unique identifier for the agent.
            agent_data: Agent configuration and state data.
        """
        self.agents[agent_id] = {
            "id": agent_id,
            "data": agent_data,
            "registered_at": datetime.utcnow(),
            "active": True
        }
        logger.info(f"Agent {agent_id} registered in simulation")
    
    def unregister_agent(self, agent_id: str) -> None:
        """
        Remove an agent from the simulation.
        
        Args:
            agent_id: Unique identifier for the agent.
        """
        if agent_id in self.agents:
            self.agents[agent_id]["active"] = False
            logger.info(f"Agent {agent_id} unregistered from simulation")
    
    def register_reality_rule(self, rule: RealityRule) -> None:
        """
        Register a reality rule.
        
        Args:
            rule: RealityRule instance to register.
        """
        self.reality_rules[rule.rule_id] = rule
        logger.info(f"Reality rule '{rule.name}' registered")
    
    def register_event_handler(
        self, 
        event_type: EventType, 
        handler: Callable[[SimulationEvent], None]
    ) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle.
            handler: Callback function to process the event.
        """
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Event handler registered for {event_type.value}")
    
    async def emit_event(self, event: SimulationEvent) -> None:
        """
        Emit an event into the simulation.
        
        Args:
            event: SimulationEvent to emit.
        """
        await self.events.put(event)
        logger.debug(f"Event emitted: {event.event_type.value} ({event.event_id})")
    
    def generate_scenario(
        self, 
        name: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> Scenario:
        """
        Generate a new procedural scenario.
        
        Args:
            name: Name of the scenario.
            parameters: Scenario-specific parameters.
            
        Returns:
            Generated Scenario instance.
        """
        scenario = Scenario(
            name=name,
            description=f"Procedurally generated scenario: {name}",
            parameters=parameters or {}
        )
        self.scenarios[scenario.scenario_id] = scenario
        logger.info(f"Scenario generated: {name} ({scenario.scenario_id})")
        return scenario
    
    def activate_scenario(self, scenario_id: str) -> None:
        """
        Activate a scenario.
        
        Args:
            scenario_id: ID of the scenario to activate.
        """
        if scenario_id not in self.scenarios:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        self.active_scenario = self.scenarios[scenario_id]
        logger.info(f"Scenario activated: {scenario_id}")
    
    def apply_reality_rules(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all active reality rules to a context.
        
        Args:
            context: Current context dictionary.
            
        Returns:
            Modified context after applying rules.
        """
        sorted_rules = sorted(
            [r for r in self.reality_rules.values() if r.active],
            key=lambda r: r.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            try:
                if rule.condition(context):
                    context = rule.effect(context)
                    logger.debug(f"Reality rule applied: {rule.name}")
            except Exception as e:
                logger.error(f"Error applying rule {rule.name}: {e}")
        
        return context
    
    def detect_anomaly(self, agent_id: str, anomaly_data: Dict[str, Any]) -> None:
        """
        Detect and record an anomaly.
        
        Args:
            agent_id: ID of the agent detecting the anomaly.
            anomaly_data: Data describing the anomaly.
        """
        anomaly = {
            "anomaly_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "detected_at": datetime.utcnow(),
            "data": anomaly_data,
            "severity": anomaly_data.get("severity", "low"),
            "resolved": False
        }
        self.anomalies.append(anomaly)
        logger.warning(f"Anomaly detected by {agent_id}: {anomaly['anomaly_id']}")
    
    async def _process_events(self) -> None:
        """Internal method to process events from the queue."""
        while self.running:
            try:
                event = await asyncio.wait_for(self.events.get(), timeout=1.0)
                
                # Apply reality rules to event data
                event.data = self.apply_reality_rules(event.data)
                
                # Call registered handlers
                handlers = self.event_handlers.get(event.event_type, [])
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")
                
                self.events.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def start(self) -> None:
        """Start the simulation engine."""
        if self.running:
            logger.warning("Simulation already running")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("Simulation engine started")
    
    async def stop(self) -> None:
        """Stop the simulation engine."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Simulation engine stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status.
        
        Returns:
            Dictionary with simulation status information.
        """
        return {
            "running": self.running,
            "active_scenario": self.active_scenario.name if self.active_scenario else None,
            "agent_count": len([a for a in self.agents.values() if a["active"]]),
            "pending_events": self.events.qsize(),
            "anomaly_count": len([a for a in self.anomalies if not a["resolved"]]),
            "reality_rules_active": len([r for r in self.reality_rules.values() if r.active])
        }
