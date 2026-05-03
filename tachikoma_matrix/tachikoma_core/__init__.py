"""
Tachikoma Core Module - Núcleo das unidades Tachikoma.

Este módulo implementa a classe base TachikomaUnit com seus atributos fundamentais:
- ghost_id: identificador único UUID
- local_memory: vetor de embeddings de memórias locais
- shared_memory_pool: referência à memória coletiva
- personality_vector: embedding evolutivo da personalidade
- autonomy_level: nível de autonomia (0.0 a 1.0)
"""

from .tachikoma_unit import TachikomaUnit
from .ghost_engine import GhostEngine
from .memory_sync import MemorySyncProtocol
from .individualization import IndividualizationEngine
from .network_protocol import NetworkProtocol
from .state_manager import StateManager

__all__ = [
    "TachikomaUnit",
    "GhostEngine",
    "MemorySyncProtocol",
    "IndividualizationEngine",
    "NetworkProtocol",
    "StateManager",
]
