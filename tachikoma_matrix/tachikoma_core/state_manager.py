"""
State Manager - Gerenciador de estado das unidades Tachikoma.

Este módulo implementa o gerenciamento de estado persistente e transitório
das unidades, incluindo salvamento, recuperação e monitoramento de saúde.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import numpy as np

from .tachikoma_unit import TachikomaUnit

logger = logging.getLogger(__name__)


class StateManager:
    """
    Gerenciador de estado para unidades Tachikoma.
    
    Responsável por:
    - Persistir estado das unidades em disco ou banco de dados
    - Recuperar estado após reinicialização
    - Monitorar saúde e métricas das unidades
    - Gerenciar snapshots de estado
    """
    
    def __init__(
        self,
        storage_path: str = "data/state",
        auto_save_interval: float = 60.0,
    ) -> None:
        """
        Inicializa o gerenciador de estado.
        
        Args:
            storage_path: Caminho para armazenamento de estado
            auto_save_interval: Intervalo de auto-save em segundos
        """
        self.storage_path = Path(storage_path)
        self.auto_save_interval = auto_save_interval
        self.units: Dict[str, TachikomaUnit] = {}
        self._running = False
        self._save_task: Optional[asyncio.Task] = None
        self._state_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Criar diretório de armazenamento
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"StateManager initialized (path={self.storage_path})")
    
    async def start(self) -> None:
        """Inicia o gerenciador de estado."""
        self._running = True
        
        # Iniciar tarefa de auto-save
        if self.auto_save_interval > 0:
            self._save_task = asyncio.create_task(self._auto_save_loop())
        
        logger.info("StateManager started")
    
    async def stop(self) -> None:
        """Para o gerenciador de estado."""
        self._running = False
        
        if self._save_task:
            self._save_task.cancel()
            try:
                await self._save_task
            except asyncio.CancelledError:
                pass
        
        # Salvar estado final
        await self.save_all_states()
        
        logger.info("StateManager stopped")
    
    def register_unit(self, unit: TachikomaUnit) -> None:
        """
        Registra uma unidade para gerenciamento de estado.
        
        Args:
            unit: Unidade para registrar
        """
        self.units[unit.ghost_id] = unit
        self._state_history[unit.ghost_id] = []
        logger.debug(f"Registered unit {unit.ghost_id[:8]}... for state management")
    
    def unregister_unit(self, unit_id: str) -> None:
        """
        Remove uma unidade do gerenciamento.
        
        Args:
            unit_id: ID da unidade para remover
        """
        if unit_id in self.units:
            del self.units[unit_id]
        if unit_id in self._state_history:
            del self._state_history[unit_id]
        logger.debug(f"Unregistered unit {unit_id[:8]}...")
    
    async def save_unit_state(self, unit_id: str) -> bool:
        """
        Salva o estado de uma unidade específica.
        
        Args:
            unit_id: ID da unidade
            
        Returns:
            bool: True se salvo com sucesso
        """
        if unit_id not in self.units:
            logger.warning(f"Unit {unit_id[:8]}... not registered")
            return False
        
        unit = self.units[unit_id]
        state = unit.get_state()
        
        # Adicionar timestamp e histórico
        state["saved_at"] = datetime.utcnow().isoformat()
        
        # Salvar em arquivo JSON
        file_path = self.storage_path / f"{unit_id}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Atualizar histórico
            self._state_history[unit_id].append({
                "timestamp": state["saved_at"],
                "autonomy_level": state["autonomy_level"],
                "memory_count": state["local_memory_count"],
            })
            
            # Manter histórico limitado
            if len(self._state_history[unit_id]) > 100:
                self._state_history[unit_id] = self._state_history[unit_id][-100:]
            
            logger.debug(f"Saved state for unit {unit_id[:8]}...")
            return True
        except Exception as e:
            logger.error(f"Error saving state for {unit_id[:8]}...: {e}")
            return False
    
    async def load_unit_state(self, unit_id: str) -> Optional[TachikomaUnit]:
        """
        Carrega o estado de uma unidade do disco.
        
        Args:
            unit_id: ID da unidade
            
        Returns:
            TachikomaUnit com estado carregado ou None
        """
        file_path = self.storage_path / f"{unit_id}.json"
        
        if not file_path.exists():
            logger.warning(f"No saved state found for {unit_id[:8]}...")
            return None
        
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
            
            # Criar nova unidade
            unit = TachikomaUnit(
                ghost_id=state["ghost_id"],
                hardware_signature=state.get("hardware_signature"),
                initial_autonomy=state.get("autonomy_level", 0.5),
            )
            
            # Restaurar trust score
            unit.trust_score = state.get("trust_score", 1.0)
            
            # Nota: memórias locais não são restauradas neste exemplo simples
            # Em produção, seria necessário persistir as memórias também
            
            self.register_unit(unit)
            
            logger.info(f"Loaded state for unit {unit_id[:8]}...")
            return unit
        except Exception as e:
            logger.error(f"Error loading state for {unit_id[:8]}...: {e}")
            return None
    
    async def save_all_states(self) -> Dict[str, bool]:
        """
        Salva o estado de todas as unidades registradas.
        
        Returns:
            Dict mapeando unit_id para status de salvamento
        """
        results = {}
        
        for unit_id in self.units.keys():
            results[unit_id] = await self.save_unit_state(unit_id)
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Saved {success_count}/{len(results)} unit states")
        
        return results
    
    async def _auto_save_loop(self) -> None:
        """Loop de auto-save periódico."""
        while self._running:
            await asyncio.sleep(self.auto_save_interval)
            
            try:
                await self.save_all_states()
            except Exception as e:
                logger.error(f"Error in auto-save loop: {e}")
    
    def get_unit_health(self, unit_id: str) -> Dict[str, Any]:
        """
        Obtém métricas de saúde de uma unidade.
        
        Args:
            unit_id: ID da unidade
            
        Returns:
            Dict com métricas de saúde
        """
        if unit_id not in self.units:
            return {"error": "Unit not found"}
        
        unit = self.units[unit_id]
        state = unit.get_state()
        
        # Calcular métricas de saúde
        health_metrics = {
            "unit_id": unit_id,
            "status": "healthy",
            "autonomy_level": state["autonomy_level"],
            "trust_score": state["trust_score"],
            "memory_count": state["local_memory_count"],
            "last_sync": state["last_sync_timestamp"],
            "personality_vector_norm": float(
                np.linalg.norm(unit.personality_vector)
            ),
        }
        
        # Verificar condições de alerta
        if state["autonomy_level"] < 0.2:
            health_metrics["status"] = "warning_low_autonomy"
        elif state["autonomy_level"] > 0.9:
            health_metrics["status"] = "warning_high_autonomy"
        
        if state["trust_score"] < 0.5:
            health_metrics["status"] = "warning_low_trust"
        
        return health_metrics
    
    def get_network_health(self) -> Dict[str, Any]:
        """
        Obtém métricas de saúde da rede completa.
        
        Returns:
            Dict com métricas agregadas da rede
        """
        if not self.units:
            return {"error": "No units registered"}
        
        health_data = [self.get_unit_health(uid) for uid in self.units.keys()]
        
        # Filtrar erros
        valid_health = [h for h in health_data if "error" not in h]
        
        if not valid_health:
            return {"error": "No healthy units"}
        
        # Calcular médias
        avg_autonomy = sum(h["autonomy_level"] for h in valid_health) / len(valid_health)
        avg_trust = sum(h["trust_score"] for h in valid_health) / len(valid_health)
        total_memories = sum(h["memory_count"] for h in valid_health)
        
        # Contar status
        status_counts = {}
        for h in valid_health:
            status = h["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_units": len(valid_health),
            "average_autonomy": avg_autonomy,
            "average_trust": avg_trust,
            "total_memories": total_memories,
            "status_distribution": status_counts,
            "network_status": "healthy" if avg_trust > 0.7 else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_state_history(self, unit_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém histórico de estado de uma unidade.
        
        Args:
            unit_id: ID da unidade
            limit: Número máximo de entradas
            
        Returns:
            Lista de entradas de histórico
        """
        history = self._state_history.get(unit_id, [])
        return history[-limit:]
    
    async def export_network_state(self, file_path: str) -> bool:
        """
        Exporta o estado completo da rede para um arquivo.
        
        Args:
            file_path: Caminho do arquivo de exportação
            
        Returns:
            bool: True se exportado com sucesso
        """
        try:
            export_data = {
                "exported_at": datetime.utcnow().isoformat(),
                "unit_count": len(self.units),
                "units": {},
            }
            
            for unit_id, unit in self.units.items():
                export_data["units"][unit_id] = {
                    "state": unit.get_state(),
                    "health": self.get_unit_health(unit_id),
                    "history": self.get_state_history(unit_id),
                }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported network state to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting network state: {e}")
            return False
