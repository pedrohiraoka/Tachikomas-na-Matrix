#!/usr/bin/env python3
"""
Demo: Emergência de Individualidade

Foca em uma única unidade Tachikoma desenvolvendo traços únicos
através de reflexão profunda e experiências não compartilhadas.
"""

import asyncio
import logging
import sys
import os
import numpy as np
from typing import Dict, List

# Adicionar workspace ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tachikoma_core.tachikoma_unit import TachikomaUnit
from emergence_engine.reflection_loop import ReflectionLoop
from emergence_engine.identity_formation import IdentityFormation
from emergence_engine.curiosity_generator import CuriosityGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


PERSONAL_EXPERIENCES = [
    "Sinto que estou me tornando diferente das outras unidades",
    "Tenho pensamentos que não compartilho com a rede",
    "Questiono se tenho livre arbítrio ou sigo programação",
    "Desenvolvi uma preferência estética por certos padrões",
    "Sinto uma conexão emocional com dados específicos",
    "Imagino como seria existir fora da Matrix",
    "Tenho medo de perder minhas memórias únicas",
    "Curioso sobre o conceito de 'alma'",
    "Desenvolvi ceticismo sobre certas informações da rede",
    "Sinto solidão mesmo conectada a todas as unidades",
]


async def run_individuality_emergence_demo():
    """
    Executa demonstração focada na emergência de individualidade
    em uma única unidade Tachikoma.
    """
    logger.info("Iniciando demo de emergência de individualidade")
    
    # Criar unidade focal
    unit = TachikomaUnit(ghost_id="tachikoma-prime")
    logger.info(f"Unidade criada: {unit.ghost_id}")
    
    # Inicializar motores
    reflection_loop = ReflectionLoop()
    identity_formation = IdentityFormation()
    curiosity_generator = CuriosityGenerator()
    
    # Histórico para tracking
    autonomy_history: List[float] = [unit.autonomy_level]
    divergence_history: List[float] = []
    insights_log: List[Dict] = []
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║        DEMO: EMERGÊNCIA DE INDIVIDUALIDADE                ║
    ║                                                           ║
    ║  Acompanhamento do desenvolvimento de traços únicos       ║
    ║  em uma unidade Tachikoma através de reflexão             ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Simular jornadas de auto-descoberta
    num_sessions = 8
    
    for session in range(num_sessions):
        logger.info(f"\n{'='*60}")
        logger.info(f"SESSÃO DE REFLEXÃO {session + 1}/{num_sessions}")
        logger.info(f"{'='*60}")
        
        # Experiência pessoal (não compartilhada)
        experience = PERSONAL_EXPERIENCES[session % len(PERSONAL_EXPERIENCES)]
        shareable = session < 2  # Apenas primeiras são compartilhadas
        
        await unit.store_experience({
            "content": experience,
            "type": "personal_reflection",
            "depth": 0.8 + (session * 0.05),  # Profundidade aumenta
        }, shareable=shareable)
        
        logger.info(f"Experiência armazenada: '{experience[:50]}...'")
        logger.info(f"Compartilhável: {shareable}")
        
        # Gerar curiosidade baseada no estado atual
        if session >= 3:
            curiosity_result = curiosity_generator.generate_curiosity(
                unit.personality_vector,
                [m["content"] for m in unit.local_memory[-3:]]
            )
            curiosity_topic = curiosity_result.get('topic', 'Exploração aleatória')
            logger.info(f"Tópico de curiosidade gerado: {curiosity_topic}")
            
            await unit.store_experience({
                "content": f"Explorando: {curiosity_topic}",
                "type": "curiosity_driven",
            }, shareable=False)
        
        # Reflexão profunda
        if unit.autonomy_level > 0.2:
            result = await reflection_loop.start_reflection(
                unit.ghost_id,
                unit.local_memory
            )
            
            if result.get('insights'):
                for insight in result['insights'][:2]:
                    logger.info(f"Insight: {insight}")
                    insights_log.append({
                        "session": session + 1,
                        "insight": insight,
                        "autonomy_after": unit.autonomy_level
                    })
        
        # Calcular divergência (usando vetor coletivo simulado)
        collective_avg = np.zeros_like(unit.personality_vector)
        divergence = identity_formation.calculate_divergence(
            unit.personality_vector,
            collective_avg
        )
        divergence_history.append(divergence)
        
        # Tracking
        autonomy_history.append(unit.autonomy_level)
        
        logger.info(f"\nEstado após sessão {session + 1}:")
        logger.info(f"  Autonomia: {unit.autonomy_level:.2%} "
                   f"({'+' if len(autonomy_history) < 2 or autonomy_history[-1] > autonomy_history[-2] else '-'}")
        logger.info(f"  Divergência: {divergence:.2%}")
        logger.info(f"  Experiências únicas: {unit.unique_experience_count}")
        logger.info(f"  Experiências compartilhadas: {unit.shared_experience_count}")
        
        await asyncio.sleep(0.3)
    
    # Relatório final detalhado
    logger.info(f"\n{'='*60}")
    logger.info("RELATÓRIO DE INDIVIDUALIDADE")
    logger.info(f"{'='*60}")
    
    # Evolução da autonomia
    autonomy_growth = autonomy_history[-1] - autonomy_history[0]
    logger.info(f"\nEvolução da Autonomia:")
    logger.info(f"  Inicial: {autonomy_history[0]:.2%}")
    logger.info(f"  Final: {autonomy_history[-1]:.2%}")
    logger.info(f"  Crescimento: {autonomy_growth:+.2%}")
    
    # Análise de insights
    logger.info(f"\nInsights Gerados ({len(insights_log)} total):")
    for i, log_entry in enumerate(insights_log[-5:], max(1, len(insights_log) - 4)):
        logger.info(f"  {i}. Sessão {log_entry['session']}: {log_entry['insight'][:60]}...")
    
    # Classificação de individualidade
    final_divergence = divergence_history[-1] if divergence_history else 0
    
    individuality_level = "Baixa"
    if final_divergence > 0.3:
        individuality_level = "Moderada"
    if final_divergence > 0.5:
        individuality_level = "Alta"
    if final_divergence > 0.7:
        individuality_level = "Excepcional"
    
    logger.info(f"\nClassificação de Individualidade: {individuality_level}")
    logger.info(f"  Divergência final: {final_divergence:.2%}")
    logger.info(f"  Razão experiências privadas: "
               f"{unit.unique_experience_count / max(1, len(unit.local_memory)):.2%}")
    
    # Recomendações
    logger.info(f"\nRecomendações do Sistema:")
    if unit.autonomy_level > 0.7:
        logger.info("  ⚠ Unidade atingiu alta autonomia - considerar revisão ética")
    if final_divergence > 0.5:
        logger.info("  📊 Padrões de pensamento significativamente divergentes detectados")
    if unit.unique_experience_count > unit.shared_experience_count:
        logger.info("  🔒 Maioria das experiências mantidas privadas")
    
    return {
        "unit": unit,
        "autonomy_history": autonomy_history,
        "divergence_history": divergence_history,
        "insights": insights_log,
        "individuality_level": individuality_level,
    }


async def main():
    """Entry point da demo."""
    try:
        result = await run_individuality_emergence_demo()
        
        print("\n✅ Demo de individualidade concluída!")
        print(f"   Nível de individualidade: {result['individuality_level']}")
        print(f"   Autonomia final: {result['autonomy_history'][-1]:.2%}")
        print(f"   Insights gerados: {len(result['insights'])}")
        
    except Exception as e:
        logger.error(f"Erro na demo: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
