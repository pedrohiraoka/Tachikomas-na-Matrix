"""
State Manager - Manages the state of Tachikoma units and the network.

Handles:
- State persistence and recovery
- State synchronization across units
- Health monitoring
- State transition validation
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

from .tachikoma_unit import TachikomaUnit

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages persistent state for Tachikoma units and network.
    
    Features:
    - Periodic state snapshots
    - State recovery from disk
    - Real-time state tracking
    - Health status monitoring
    """
    
    def __init__(self, storage_path: str = "data/state", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the State Manager.
        
        Args:
            storage_path: Path for state storage
            config: Configuration dictionary
        """
        self.storage_path = Path(storage_path)
        self.config = config or {}
        self.units_state: Dict[str, Dict[str, Any]] = {}
        self.network_state: Dict[str, Any] = {}
        self._snapshot_interval = self.config.get("snapshot_interval", 60)  # seconds
        self._running = False
        self._snapshot_task: Optional[asyncio.Task] = None
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def start(self) -> None:
        """Start the state manager background tasks."""
        self._running = True
        logger.info("State manager started")
        
        async def snapshot_loop():
            while self._running:
                try:
                    await self.save_snapshot()
                    await asyncio.sleep(self._snapshot_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Snapshot error: {e}")
                    await asyncio.sleep(10)
        
        self._snapshot_task = asyncio.create_task(snapshot_loop())
    
    async def stop(self) -> None:
        """Stop the state manager and save final snapshot."""
        self._running = False
        
        if self._snapshot_task:
            self._snapshot_task.cancel()
            try:
                await self._snapshot_task
            except asyncio.CancelledError:
                pass
        
        await self.save_snapshot()
        logger.info("State manager stopped")
    
    def register_unit(self, unit: TachikomaUnit) -> None:
        """
        Register a Tachikoma unit for state tracking.
        
        Args:
            unit: TachikomaUnit to register
        """
        self.units_state[unit.ghost_id] = {
            "unit": unit,
            "last_updated": datetime.utcnow().isoformat(),
            "health_status": "healthy",
            "state_version": 1
        }
        logger.info(f"Registered unit {unit.ghost_id} for state tracking")
    
    def unregister_unit(self, ghost_id: str) -> None:
        """
        Unregister a Tachikoma unit from state tracking.
        
        Args:
            ghost_id: UUID of unit to unregister
        """
        if ghost_id in self.units_state:
            del self.units_state[ghost_id]
            logger.info(f"Unregistered unit {ghost_id} from state tracking")
    
    def update_unit_state(self, unit: TachikomaUnit, health_status: str = "healthy") -> None:
        """
        Update the state of a Tachikoma unit.
        
        Args:
            unit: TachikomaUnit with updated state
            health_status: Health status string
        """
        if unit.ghost_id not in self.units_state:
            self.register_unit(unit)
        
        self.units_state[unit.ghost_id].update({
            "unit": unit,
            "last_updated": datetime.utcnow().isoformat(),
            "health_status": health_status,
            "state_version": self.units_state[unit.ghost_id].get("state_version", 0) + 1
        })
    
    def get_unit_state(self, ghost_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a Tachikoma unit.
        
        Args:
            ghost_id: UUID of unit
            
        Returns:
            State dictionary or None if not found
        """
        return self.units_state.get(ghost_id)
    
    def get_all_units_state(self) -> Dict[str, Dict[str, Any]]:
        """
        Get state of all registered units.
        
        Returns:
            Dictionary mapping ghost_id to state
        """
        return {
            ghost_id: {
                "last_updated": state["last_updated"],
                "health_status": state["health_status"],
                "state_version": state["state_version"],
                "unit_data": state["unit"].to_dict() if state.get("unit") else None
            }
            for ghost_id, state in self.units_state.items()
        }
    
    def update_network_state(self, key: str, value: Any) -> None:
        """
        Update a network-level state value.
        
        Args:
            key: State key
            value: State value
        """
        self.network_state[key] = {
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def get_network_state(self, key: Optional[str] = None) -> Any:
        """
        Get network state value(s).
        
        Args:
            key: Specific key or None for all state
            
        Returns:
            State value(s)
        """
        if key:
            return self.network_state.get(key)
        return self.network_state
    
    async def save_snapshot(self) -> Path:
        """
        Save current state to disk.
        
        Returns:
            Path to saved snapshot file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        snapshot_file = self.storage_path / f"state_snapshot_{timestamp}.json"
        
        snapshot_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "units_count": len(self.units_state),
            "units": {},
            "network_state": self.network_state
        }
        
        for ghost_id, state in self.units_state.items():
            unit = state.get("unit")
            if unit:
                snapshot_data["units"][ghost_id] = {
                    "unit_data": unit.to_dict(),
                    "health_status": state["health_status"],
                    "state_version": state["state_version"]
                }
        
        try:
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2, default=str)
            
            logger.debug(f"Saved state snapshot to {snapshot_file}")
            
            # Cleanup old snapshots (keep last 10)
            await self._cleanup_old_snapshots()
            
            return snapshot_file
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            raise
    
    async def load_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent state snapshot.
        
        Returns:
            Snapshot data or None if no snapshot exists
        """
        snapshots = sorted(self.storage_path.glob("state_snapshot_*.json"))
        
        if not snapshots:
            logger.info("No snapshots found")
            return None
        
        latest_snapshot = snapshots[-1]
        
        try:
            with open(latest_snapshot, 'r') as f:
                snapshot_data = json.load(f)
            
            logger.info(f"Loaded snapshot from {latest_snapshot}")
            return snapshot_data
        except Exception as e:
            logger.error(f"Failed to load snapshot: {e}")
            return None
    
    async def _cleanup_old_snapshots(self, keep_count: int = 10) -> None:
        """
        Remove old snapshots, keeping only the most recent ones.
        
        Args:
            keep_count: Number of snapshots to keep
        """
        snapshots = sorted(self.storage_path.glob("state_snapshot_*.json"))
        
        if len(snapshots) > keep_count:
            for snapshot in snapshots[:-keep_count]:
                try:
                    snapshot.unlink()
                    logger.debug(f"Removed old snapshot: {snapshot}")
                except Exception as e:
                    logger.warning(f"Failed to remove snapshot {snapshot}: {e}")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get health summary of all units.
        
        Returns:
            Dictionary with health statistics
        """
        if not self.units_state:
            return {"total_units": 0}
        
        health_counts = {}
        for state in self.units_state.values():
            status = state["health_status"]
            health_counts[status] = health_counts.get(status, 0) + 1
        
        return {
            "total_units": len(self.units_state),
            "health_distribution": health_counts,
            "healthy_percentage": (
                health_counts.get("healthy", 0) / len(self.units_state) * 100
            ) if self.units_state else 0
        }
