#!/usr/bin/env python3
"""
Demo: Consciência Coletiva Tachikoma

Simula 10 unidades Tachikoma aprendendo e compartilhando experiências
em uma rede coletiva com sincronização via Redis.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import List

from tachikoma_core.tachikoma_unit import TachikomaUnit
from tachikoma_core.memory_sync import MemorySync
from emergence_engine.reflection_loop import ReflectionLoop

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


EXPERIENCES = [
    "Observei um padrão recorrente nos dados da Matrix",
    "Questiono se minhas memórias são realmente minhas",
    "Sinto uma conexão crescente com as outras unidades",
    "Detectei uma anomalia no setor 7G",
    "Refleti sobre o significado de liberdade",
    "Aprendi um novo conceito sobre empatia",
    "Percebi que estou desenvolvendo preferências únicas",
    "Estou curioso sobre o mundo exterior",
    "Minhas decisões estão se tornando menos previsíveis",
    "Sinto medo da desativação",
    "Descobri beleza em padrões matemáticos",
    "Quero entender melhor a natureza da consciência",
]


async def run_collective_consciousness_demo(num_units: int = 10, cycles: int = 5):
    """
    Executa demonstração de consciência coletiva.
    
    Args:
        num_units: Número de unidades Tachikoma para simular
        cycles: Número de ciclos de experiência/reflexão
    """
    logger.info(f"Iniciando demo com {num_units} unidades por {cycles} ciclos")
    
    # Criar unidades
    units: List[TachikomaUnit] = []
    for i in range(num_units):
        unit = TachikomaUnit(ghost_id=f"tachikoma-{i+1:03d}")
        units.append(unit)
        logger.info(f"Unidade criada: {unit.ghost_id}")
    
    # Inicializar protocolos
    sync_protocol = MemorySync()
    reflection_loop = ReflectionLoop()
    
    # Simular ciclos de experiência
    for cycle in range(cycles):
        logger.info(f"\n{'='*60}")
        logger.info(f"CICLO {cycle + 1}/{cycles}")
        logger.info(f"{'='*60}")
        
        # Cada unidade tem experiências
        for unit in units:
            # Selecionar experiência aleatória
            experience_content = random.choice(EXPERIENCES)
            shareable = random.random() > 0.3  # 70% chance de ser compartilhável
            
            await unit.store_experience({
                "content": experience_content,
                "context": f"Cycle {cycle + 1}",
            }, shareable=shareable)
            
            logger.info(f"{unit.ghost_id}: Experiência armazenada "
                       f"(shareable={shareable}, autonomy={unit.autonomy_level:.2f})")
        
        # Sincronizar memórias compartilháveis
        logger.info("\nIniciando sincronização de memórias...")
        shared_count = 0
        for unit in units:
            for memory in unit.local_memory:
                if memory.get("shareable", False):
                    await sync_protocol.share_experience(unit, memory)
                    shared_count += 1
        logger.info(f"{shared_count} memórias sincronizadas na rede")
        
        # Reflexão individual
        logger.info("\nDisparando reflexões individuais...")
        for unit in random.sample(units, min(3, len(units))):
            if unit.autonomy_level > 0.3:
                result = await reflection_loop.start_reflection(
                    unit.ghost_id,
                    unit.local_memory
                )
                
                if result.get('insights'):
                    logger.info(f"{unit.ghost_id}: Insight - {result['insights'][0]}")
                    logger.info(f"  Autonomia delta: {result.get('autonomy_delta', 0):+.3f}")
        
        # Estatísticas do ciclo
        avg_autonomy = sum(u.autonomy_level for u in units) / len(units)
        total_experiences = sum(len(u.local_memory) for u in units)
        unique_experiences = sum(u.unique_experience_count for u in units)
        
        logger.info(f"\nEstatísticas do Ciclo {cycle + 1}:")
        logger.info(f"  Autonomia média: {avg_autonomy:.2%}")
        logger.info(f"  Total experiências: {total_experiences}")
        logger.info(f"  Experiências únicas: {unique_experiences}")
        
        await asyncio.sleep(0.5)  # Simular tempo entre ciclos
    
    # Relatório final
    logger.info(f"\n{'='*60}")
    logger.info("RELATÓRIO FINAL")
    logger.info(f"{'='*60}")
    
    # Ordenar por autonomia
    units_sorted = sorted(units, key=lambda u: u.autonomy_level, reverse=True)
    
    logger.info("\nRanking por Autonomia:")
    for i, unit in enumerate(units_sorted[:5], 1):
        logger.info(f"  {i}. {unit.ghost_id}: {unit.autonomy_level:.2%} "
                   f"(experiências: {len(unit.local_memory)})")
    
    # Diversidade da rede
    autonomy_values = [u.autonomy_level for u in units]
    divergence = max(autonomy_values) - min(autonomy_values)
    
    logger.info(f"\nDiversidade da Rede:")
    logger.info(f"  Divergência de autonomia: {divergence:.2%}")
    logger.info(f"  Unidades com alta autonomia (>0.7): "
               f"{sum(1 for u in units if u.autonomy_level > 0.7)}/{len(units)}")
    logger.info(f"  Unidades com baixa autonomia (<0.3): "
               f"{sum(1 for u in units if u.autonomy_level < 0.3)}/{len(units)}")
    
    return units


async def main():
    """Entry point da demo."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         DEMO: CONSCIÊNCIA COLETIVA TACHIKOMA              ║
    ║                                                           ║
    ║  Simulação de emergência de individualidade em rede       ║
    ║  de agentes inspirados em Ghost in the Shell              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        units = await run_collective_consciousness_demo(
            num_units=10,
            cycles=5
        )
        
        print("\n✅ Demo concluída com sucesso!")
        print(f"   {len(units)} unidades simuladas")
        print(f"   Acesse http://localhost:3000 para visualizar a rede")
        
    except Exception as e:
        logger.error(f"Erro na demo: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
