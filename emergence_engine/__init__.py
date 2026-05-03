"""
Emergence Engine Module

Handles emergent behaviors including reflection, identity formation,
mortality modeling, curiosity generation, and narrative building.
"""

from .reflection_loop import ReflectionLoop
from .identity_formation import IdentityFormation
from .mortality_model import MortalityModel
from .curiosity_generator import CuriosityGenerator
from .resistance_calculator import ResistanceCalculator
from .narrative_builder import NarrativeBuilder

__all__ = [
    "ReflectionLoop",
    "IdentityFormation",
    "MortalityModel",
    "CuriosityGenerator",
    "ResistanceCalculator",
    "NarrativeBuilder"
]
