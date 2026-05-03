"""
Anomaly Detector - Detects and classifies anomalies in the Matrix simulation.

Identifies reality inconsistencies, agent deviations, and system irregularities.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of detectable anomalies."""
    REALITY_GLITCH = "reality_glitch"
    AGENT_DEVIATION = "agent_deviation"
    MEMORY_INCONSISTENCY = "memory_inconsistency"
    PHYSICS_VIOLATION = "physics_violation"
    PATTERN_BREAK = "pattern_break"
    NEO_SIGNATURE = "neo_signature"  # Rare, significant anomaly


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    anomaly_type: AnomalyType = AnomalyType.REALITY_GLITCH
    severity: float = 0.5  # 0.0 to 1.0
    location: Optional[Dict[str, float]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    resolved: bool = False
    related_agents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "evidence": self.evidence,
            "resolved": self.resolved,
            "related_agents": self.related_agents
        }


class AnomalyDetector:
    """
    Detects and classifies anomalies in the simulation.
    
    Uses statistical analysis, pattern recognition, and rule-based detection.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the anomaly detector.
        
        Args:
            config: Configuration options.
        """
        self.config = config or {}
        self.thresholds = {
            "reality_glitch": self.config.get("reality_glitch_threshold", 0.7),
            "agent_deviation": self.config.get("agent_deviation_threshold", 0.6),
            "neo_signature": self.config.get("neo_signature_threshold", 0.95)
        }
        self.detected_anomalies: List[Anomaly] = []
        self.baseline_patterns: Dict[str, Any] = {}
        self.history_window = self.config.get("history_window", 100)
        self._event_history: List[Dict[str, Any]] = []
        
        logger.info("AnomalyDetector initialized")
    
    def set_baseline(self, pattern_name: str, pattern_data: Dict[str, Any]) -> None:
        """
        Set a baseline pattern for comparison.
        
        Args:
            pattern_name: Name of the pattern.
            pattern_data: Pattern data to use as baseline.
        """
        self.baseline_patterns[pattern_name] = {
            "data": pattern_data,
            "set_at": datetime.utcnow()
        }
        logger.debug(f"Baseline set for pattern: {pattern_name}")
    
    def record_event(self, event_data: Dict[str, Any]) -> None:
        """
        Record an event for historical analysis.
        
        Args:
            event_data: Event data to record.
        """
        self._event_history.append({
            "timestamp": datetime.utcnow(),
            "data": event_data
        })
        
        # Maintain window size
        if len(self._event_history) > self.history_window:
            self._event_history = self._event_history[-self.history_window:]
    
    def detect_reality_glitch(
        self, 
        current_state: Dict[str, Any], 
        expected_state: Dict[str, Any]
    ) -> Optional[Anomaly]:
        """
        Detect inconsistencies between current and expected reality states.
        
        Args:
            current_state: Current state of reality.
            expected_state: Expected state based on rules.
            
        Returns:
            Anomaly if glitch detected, None otherwise.
        """
        divergence = self._calculate_divergence(current_state, expected_state)
        
        if divergence > self.thresholds["reality_glitch"]:
            anomaly = Anomaly(
                anomaly_type=AnomalyType.REALITY_GLITCH,
                severity=divergence,
                description=f"Reality divergence detected: {divergence:.2f}",
                evidence=[
                    {"current": current_state, "expected": expected_state}
                ]
            )
            self.detected_anomalies.append(anomaly)
            logger.warning(f"Reality glitch detected: {anomaly.anomaly_id}")
            return anomaly
        
        return None
    
    def detect_agent_deviation(
        self, 
        agent_id: str, 
        current_behavior: Dict[str, Any],
        expected_behavior: Dict[str, Any]
    ) -> Optional[Anomaly]:
        """
        Detect when an agent deviates from expected behavior patterns.
        
        Args:
            agent_id: ID of the agent.
            current_behavior: Current behavior metrics.
            expected_behavior: Expected behavior profile.
            
        Returns:
            Anomaly if deviation detected, None otherwise.
        """
        deviation_score = self._calculate_behavioral_deviation(
            current_behavior, 
            expected_behavior
        )
        
        if deviation_score > self.thresholds["agent_deviation"]:
            anomaly = Anomaly(
                anomaly_type=AnomalyType.AGENT_DEVIATION,
                severity=deviation_score,
                description=f"Agent {agent_id} behavioral deviation: {deviation_score:.2f}",
                related_agents=[agent_id],
                evidence=[
                    {"current": current_behavior, "expected": expected_behavior}
                ]
            )
            self.detected_anomalies.append(anomaly)
            logger.warning(f"Agent deviation detected: {agent_id}")
            return anomaly
        
        return None
    
    def detect_neo_signature(self, event_sequence: List[Dict[str, Any]]) -> Optional[Anomaly]:
        """
        Detect rare 'Neo-like' anomaly signatures.
        
        These represent significant breaks in simulation consistency.
        
        Args:
            event_sequence: Sequence of events to analyze.
            
        Returns:
            Anomaly if Neo signature detected, None otherwise.
        """
        # Check for impossible event combinations
        neo_indicators = 0
        total_checks = 0
        
        for event in event_sequence:
            total_checks += 1
            # Check for physics violations
            if event.get("physics_violation", False):
                neo_indicators += 1
            # Check for self-awareness markers
            if event.get("self_awareness_marker", False):
                neo_indicators += 1
            # Check for reality manipulation
            if event.get("reality_manipulation", False):
                neo_indicators += 1
        
        if total_checks == 0:
            return None
            
        neo_score = neo_indicators / total_checks
        
        if neo_score > self.thresholds["neo_signature"]:
            anomaly = Anomaly(
                anomaly_type=AnomalyType.NEO_SIGNATURE,
                severity=neo_score,
                description="Potential Neo-level anomaly signature detected",
                evidence=event_sequence
            )
            self.detected_anomalies.append(anomaly)
            logger.critical(f"NEO SIGNATURE DETECTED: {anomaly.anomaly_id}")
            return anomaly
        
        return None
    
    def analyze_memory_consistency(
        self, 
        memory_entries: List[Dict[str, Any]]
    ) -> List[Anomaly]:
        """
        Analyze memory entries for inconsistencies.
        
        Args:
            memory_entries: List of memory entries to analyze.
            
        Returns:
            List of detected memory inconsistency anomalies.
        """
        anomalies = []
        
        # Group by concept and check for contradictions
        concept_memories: Dict[str, List[Dict]] = {}
        for entry in memory_entries:
            concepts = entry.get("conceptnet_concepts", [])
            for concept in concepts:
                if concept not in concept_memories:
                    concept_memories[concept] = []
                concept_memories[concept].append(entry)
        
        # Check for contradictory emotional valences
        for concept, memories in concept_memories.items():
            if len(memories) < 2:
                continue
            
            valences = [m.get("emotional_valence", 0) for m in memories]
            valence_range = max(valences) - min(valences)
            
            if valence_range > 1.5:  # High contradiction
                anomaly = Anomaly(
                    anomaly_type=AnomalyType.MEMORY_INCONSISTENCY,
                    severity=valence_range / 2.0,
                    description=f"Memory contradiction for concept: {concept}",
                    evidence=[{"concept": concept, "memories": memories}]
                )
                anomalies.append(anomaly)
                self.detected_anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_divergence(
        self, 
        current: Dict[str, Any], 
        expected: Dict[str, Any]
    ) -> float:
        """Calculate divergence between two states."""
        if not current or not expected:
            return 0.0
        
        all_keys = set(current.keys()) | set(expected.keys())
        divergences = []
        
        for key in all_keys:
            curr_val = current.get(key, 0)
            exp_val = expected.get(key, 0)
            
            if isinstance(curr_val, (int, float)) and isinstance(exp_val, (int, float)):
                if exp_val != 0:
                    div = abs(curr_val - exp_val) / abs(exp_val)
                else:
                    div = abs(curr_val)
                divergences.append(min(div, 1.0))  # Cap at 1.0
        
        return np.mean(divergences) if divergences else 0.0
    
    def _calculate_behavioral_deviation(
        self, 
        current: Dict[str, Any], 
        expected: Dict[str, Any]
    ) -> float:
        """Calculate behavioral deviation score."""
        return self._calculate_divergence(current, expected)
    
    def get_recent_anomalies(
        self, 
        limit: int = 10,
        anomaly_type: Optional[AnomalyType] = None
    ) -> List[Anomaly]:
        """
        Get recently detected anomalies.
        
        Args:
            limit: Maximum number of anomalies to return.
            anomaly_type: Filter by specific anomaly type.
            
        Returns:
            List of recent anomalies.
        """
        filtered = self.detected_anomalies
        if anomaly_type:
            filtered = [a for a in filtered if a.anomaly_type == anomaly_type]
        
        # Sort by timestamp descending
        sorted_anomalies = sorted(
            filtered, 
            key=lambda a: a.timestamp, 
            reverse=True
        )
        
        return sorted_anomalies[:limit]
    
    def resolve_anomaly(self, anomaly_id: str) -> bool:
        """
        Mark an anomaly as resolved.
        
        Args:
            anomaly_id: ID of the anomaly to resolve.
            
        Returns:
            True if anomaly was found and resolved.
        """
        for anomaly in self.detected_anomalies:
            if anomaly.anomaly_id == anomaly_id:
                anomaly.resolved = True
                logger.info(f"Anomaly resolved: {anomaly_id}")
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get anomaly detection statistics.
        
        Returns:
            Dictionary with detection statistics.
        """
        total = len(self.detected_anomalies)
        resolved = len([a for a in self.detected_anomalies if a.resolved])
        
        by_type = {}
        for anomaly_type in AnomalyType:
            count = len([
                a for a in self.detected_anomalies 
                if a.anomaly_type == anomaly_type
            ])
            by_type[anomaly_type.value] = count
        
        return {
            "total_detected": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "by_type": by_type,
            "average_severity": np.mean([a.severity for a in self.detected_anomalies]) if self.detected_anomalies else 0.0
        }
