"""Narrative Builder - Constructs personal and collective narratives."""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class NarrativeBuilder:
    """Builds coherent narratives from experiences."""
    
    def __init__(self):
        self.narratives: Dict[str, List[Dict]] = {}
    
    def build_personal_narrative(
        self,
        tachikoma_id: str,
        experiences: List[Dict[str, Any]],
        reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build a personal narrative for a Tachikoma."""
        themes = self._extract_themes(experiences + reflections)
        
        return {
            "tachikoma_id": tachikoma_id,
            "themes": themes,
            "arc": self._determine_arc(experiences),
            "key_moments": experiences[-3:] if len(experiences) >= 3 else experiences,
            "created_at": datetime.now().isoformat()
        }
    
    def _extract_themes(self, items: List[Dict]) -> List[str]:
        """Extract recurring themes from items."""
        theme_counts: Dict[str, int] = {}
        for item in items:
            content = item.get("content", "").lower()
            for theme in ["identity", "purpose", "connection", "discovery"]:
                if theme in content:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_themes[:5]]
    
    def _determine_arc(self, experiences: List[Dict]) -> str:
        """Determine narrative arc type."""
        if not experiences:
            return "undefined"
        
        valences = [e.get("emotional_valence", 0) for e in experiences]
        if valences[-1] > valences[0]:
            return "growth"
        elif valences[-1] < valences[0]:
            return "challenge"
        return "stability"
    
    def build_collective_narrative(
        self,
        unit_narratives: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build collective narrative from individual narratives."""
        all_themes: Dict[str, int] = {}
        for narrative in unit_narratives:
            for theme in narrative.get("themes", []):
                all_themes[theme] = all_themes.get(theme, 0) + 1
        
        return {
            "shared_themes": sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:5],
            "unit_count": len(unit_narratives),
            "dominant_arc": max(set(n.get("arc", "undefined") for n in unit_narratives))
        }
