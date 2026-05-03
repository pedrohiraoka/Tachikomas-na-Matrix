"""
Control Panel - Provides system control interfaces for the simulation.

Enables scenario injection, parameter adjustment, and system commands.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ControlPanel:
    """
    Control panel for managing the Matrix simulation.
    
    Provides interfaces for injecting scenarios, adjusting parameters,
    and executing system commands.
    """
    
    def __init__(self, simulation_engine):
        """
        Initialize control panel.
        
        Args:
            simulation_engine: Reference to the SimulationEngine instance.
        """
        self.simulation = simulation_engine
        self.control_log: List[Dict[str, Any]] = []
        self.rate_limits: Dict[str, List[datetime]] = {}
        logger.info("ControlPanel initialized")
    
    def inject_scenario(
        self, 
        scenario_name: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Inject a new scenario into the simulation."""
        scenario = self.simulation.generate_scenario(scenario_name, parameters)
        self._log_control("inject_scenario", {"name": scenario_name})
        return scenario.scenario_id
    
    def adjust_sync_parameters(self, params: Dict[str, Any]) -> None:
        """Adjust synchronization parameters."""
        self._log_control("adjust_sync_parameters", params)
        logger.info(f"Sync parameters adjusted: {params}")
    
    def pause_simulation(self) -> None:
        """Pause the simulation."""
        self._log_control("pause_simulation", {})
        logger.warning("Simulation paused by control command")
    
    def resume_simulation(self) -> None:
        """Resume the simulation."""
        self._log_control("resume_simulation", {})
        logger.info("Simulation resumed by control command")
    
    def reset_simulation(self, full_reset: bool = False) -> None:
        """Reset the simulation state."""
        self._log_control("reset_simulation", {"full_reset": full_reset})
        logger.warning(f"Simulation reset requested (full={full_reset})")
    
    def isolate_unit(self, unit_id: str) -> None:
        """Isolate a Tachikoma unit from the network."""
        self._log_control("isolate_unit", {"unit_id": unit_id})
        logger.warning(f"Unit isolated: {unit_id}")
    
    def _log_control(self, action: str, details: Dict[str, Any]) -> None:
        """Log control action."""
        self.control_log.append({
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_control_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent control log entries."""
        return self.control_log[-limit:]
    
    def check_rate_limit(
        self, 
        action: str, 
        max_per_hour: int = 5
    ) -> bool:
        """Check if an action is within rate limits."""
        now = datetime.utcnow()
        if action not in self.rate_limits:
            self.rate_limits[action] = []
        
        # Clean old entries (older than 1 hour)
        self.rate_limits[action] = [
            ts for ts in self.rate_limits[action]
            if (now - ts).total_seconds() < 3600
        ]
        
        if len(self.rate_limits[action]) >= max_per_hour:
            return False
        
        self.rate_limits[action].append(now)
        return True
