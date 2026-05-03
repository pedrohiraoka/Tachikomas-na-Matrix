"""
Reality Layer - Manages different layers of simulated reality.

Provides configurable reality rules and state management.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
import uuid

logger = logging.getLogger(__name__)


@dataclass
class RealityState:
    """Represents the current state of a reality layer."""
    layer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Reality"
    physical_constants: Dict[str, float] = field(default_factory=dict)
    active_rules: List[str] = field(default_factory=list)
    stability: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RealityLayer:
    """Manages a layer of simulated reality with configurable rules."""
    
    def __init__(self, name: str = "Default Reality"):
        self.name = name
        self.state = RealityState(name=name)
        self.rules: Dict[str, Dict[str, Any]] = {}
        logger.info(f"RealityLayer created: {name}")
    
    def set_physical_constant(self, name: str, value: float) -> None:
        """Set a physical constant for this reality layer."""
        self.state.physical_constants[name] = value
        logger.debug(f"Physical constant set: {name}={value}")
    
    def add_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> None:
        """Add a reality rule."""
        self.rules[rule_id] = rule_data
        if rule_id not in self.state.active_rules:
            self.state.active_rules.append(rule_id)
        logger.info(f"Rule added to {self.name}: {rule_id}")
    
    def remove_rule(self, rule_id: str) -> None:
        """Remove a reality rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
        if rule_id in self.state.active_rules:
            self.state.active_rules.remove(rule_id)
        logger.info(f"Rule removed from {self.name}: {rule_id}")
    
    def apply_rules(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all active rules to a context."""
        for rule_id in self.state.active_rules:
            rule = self.rules.get(rule_id, {})
            if rule.get("active", True):
                condition = rule.get("condition")
                effect = rule.get("effect")
                if condition and effect:
                    try:
                        if condition(context):
                            context = effect(context)
                    except Exception as e:
                        logger.error(f"Error applying rule {rule_id}: {e}")
        return context
    
    def get_state(self) -> Dict[str, Any]:
        """Get current reality state."""
        return {
            "layer_id": self.state.layer_id,
            "name": self.state.name,
            "physical_constants": self.state.physical_constants,
            "active_rules": self.state.active_rules,
            "stability": self.state.stability,
            "timestamp": self.state.timestamp.isoformat()
        }
