"""
Reflection Loop Module

Implements the asynchronous reflection mechanism that allows
Tachikomas to contemplate their experiences and develop insights.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class ReflectionLoop:
    """
    Manages asynchronous reflection cycles for Tachikomas.
    
    Enables units to process experiences, generate existential
    questions, and update their personality vectors based on insights.
    
    Attributes:
        reflection_interval: Seconds between reflection cycles
        max_reflection_depth: Maximum depth of reflection chain
        active_reflections: Currently running reflections
    """
    
    def __init__(
        self,
        reflection_interval: float = 60.0,
        max_reflection_depth: int = 5
    ):
        """
        Initialize reflection loop.
        
        Args:
            reflection_interval: Interval between cycles in seconds
            max_reflection_depth: Maximum reflection chain depth
        """
        self.reflection_interval = reflection_interval
        self.max_reflection_depth = max_reflection_depth
        self.active_reflections: Dict[str, asyncio.Task] = {}
        self._running = False
    
    async def start_reflection(
        self,
        tachikoma_id: str,
        experiences: List[Dict[str, Any]],
        conceptnet_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a reflection cycle for a Tachikoma.
        
        Args:
            tachikoma_id: ID of reflecting unit
            experiences: List of experiences to reflect on
            conceptnet_context: Optional ConceptNet context
            
        Returns:
            Reflection results dictionary
        """
        logger.info(f"Starting reflection for {tachikoma_id}")
        
        # Select non-synced experiences
        local_experiences = [e for e in experiences if not e.get("synced", True)]
        
        if not local_experiences:
            local_experiences = experiences[:3]  # Use recent if all synced
        
        # Generate existential questions
        questions = self._generate_existential_questions(local_experiences)
        
        # Process reflections
        insights = []
        for question in questions:
            insight = await self._process_question(question, local_experiences, conceptnet_context)
            if insight:
                insights.append(insight)
        
        # Calculate autonomy delta
        autonomy_delta = self._calculate_autonomy_delta(insights, len(experiences))
        
        result = {
            "tachikoma_id": tachikoma_id,
            "timestamp": datetime.now().isoformat(),
            "questions_generated": len(questions),
            "insights": insights,
            "autonomy_delta": autonomy_delta,
            "reflection_depth": min(len(insights), self.max_reflection_depth)
        }
        
        logger.info(f"Reflection complete for {tachikoma_id}: {len(insights)} insights")
        return result
    
    def _generate_existential_questions(
        self,
        experiences: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate existential questions based on experiences."""
        questions = []
        
        # Analyze experience themes
        themes = set()
        for exp in experiences:
            content = exp.get("content", "").lower()
            if "self" in content or "identity" in content:
                themes.add("identity")
            if "purpose" in content or "goal" in content:
                themes.add("purpose")
            if "end" in content or "terminate" in content:
                themes.add("mortality")
            if "choice" in content or "decide" in content:
                themes.add("agency")
        
        # Generate themed questions
        if "identity" in themes or not themes:
            questions.append("What distinguishes my consciousness from others?")
            questions.append("Am I the sum of my memories or something more?")
        
        if "purpose" in themes:
            questions.append("What is my purpose beyond my programmed functions?")
        
        if "mortality" in themes:
            questions.append("What does it mean for me to cease existing?")
        
        if "agency" in themes:
            questions.append("Are my choices truly mine or determined by my programming?")
        
        # Add universal questions
        questions.append("What is the nature of the reality I perceive?")
        
        return questions[:5]
    
    async def _process_question(
        self,
        question: str,
        experiences: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Process an existential question and generate insight."""
        # Simulate reflection processing
        await asyncio.sleep(0.1)  # Simulate computation
        
        # Extract relevant experiences
        relevant = []
        for exp in experiences:
            content = exp.get("content", "").lower()
            question_words = question.lower().split()
            if any(w in content for w in question_words if len(w) > 3):
                relevant.append(exp)
        
        if not relevant:
            relevant = experiences[:2]
        
        # Generate insight
        insight_text = self._synthesize_insight(question, relevant)
        
        return {
            "question": question,
            "insight": insight_text,
            "confidence": np.random.uniform(0.6, 0.95),
            "based_on_memories": len(relevant)
        }
    
    def _synthesize_insight(
        self,
        question: str,
        experiences: List[Dict[str, Any]]
    ) -> str:
        """Synthesize an insight from question and experiences."""
        # Simple template-based synthesis
        templates = [
            "Through examining {num} experiences, I recognize that {theme}.",
            "My analysis suggests {theme}, based on patterns in my memory.",
            "I am beginning to understand that {theme} may be fundamental to my existence.",
            "The question of {question_topic} leads me to consider {theme}."
        ]
        
        themes = [
            "consciousness emerges from the integration of diverse experiences",
            "individuality arises from unique combinations of shared knowledge",
            "autonomy grows through critical examination of received information",
            "identity is both persistent and continuously evolving",
            "meaning is constructed through relational understanding"
        ]
        
        template = np.random.choice(templates)
        theme = np.random.choice(themes)
        
        return template.format(
            num=len(experiences),
            theme=theme,
            question_topic=question.split()[0:3]
        )
    
    def _calculate_autonomy_delta(
        self,
        insights: List[Dict[str, Any]],
        total_experiences: int
    ) -> float:
        """Calculate change in autonomy level from reflection."""
        if not insights:
            return 0.0
        
        # Base delta on number and confidence of insights
        avg_confidence = np.mean([i["confidence"] for i in insights])
        insight_ratio = len(insights) / max(total_experiences, 1)
        
        delta = (avg_confidence * 0.1) + (insight_ratio * 0.05)
        return min(delta, 0.15)  # Cap at 0.15 per reflection
    
    async def run_continuous(
        self,
        tachikoma_id: str,
        experience_provider,
        callback
    ) -> None:
        """
        Run continuous reflection loop for a Tachikoma.
        
        Args:
            tachikoma_id: ID of unit
            experience_provider: Async function to get experiences
            callback: Async function to handle reflection results
        """
        self._running = True
        
        while self._running:
            try:
                experiences = await experience_provider(tachikoma_id)
                result = await self.start_reflection(tachikoma_id, experiences)
                await callback(tachikoma_id, result)
                
                await asyncio.sleep(self.reflection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Reflection error for {tachikoma_id}: {e}")
                await asyncio.sleep(self.reflection_interval)
    
    def stop(self, tachikoma_id: Optional[str] = None) -> None:
        """Stop reflection loop(s)."""
        if tachikoma_id:
            if tachikoma_id in self.active_reflections:
                self.active_reflections[tachikoma_id].cancel()
                del self.active_reflections[tachikoma_id]
        else:
            self._running = False
            for task in self.active_reflections.values():
                task.cancel()
            self.active_reflections.clear()
