"""
Main entry point for Tachikoma Matrix simulation.

Usage:
    python main.py --config config/production.yaml --mode simulation
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tachikoma_core.tachikoma_unit import TachikomaUnit
from tachikoma_core.ghost_engine import GhostEngine
from tachikoma_core.memory_sync import MemorySyncProtocol, SharedMemoryPool
from tachikoma_core.individualization import IndividualizationEngine
from tachikoma_core.state_manager import StateManager
from knowledge_engine.conceptnet_loader import ConceptNetLoader


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


async def run_simulation(num_units: int = 10, duration_seconds: int = 60) -> None:
    """
    Run the Tachikoma Matrix simulation.
    
    Args:
        num_units: Number of Tachikoma units to simulate
        duration_seconds: How long to run the simulation
    """
    logger = logging.getLogger("simulation")
    logger.info(f"Starting simulation with {num_units} units for {duration_seconds}s")
    
    # Initialize components
    conceptnet = ConceptNetLoader()
    await conceptnet.load_embeddings()
    
    shared_pool = SharedMemoryPool(max_size=10000)
    sync_protocol = MemorySyncProtocol()
    sync_protocol.set_shared_pool(shared_pool)
    
    ghost_engine = GhostEngine()
    individualization = IndividualizationEngine()
    state_manager = StateManager()
    
    await state_manager.start()
    
    # Create Tachikoma units
    units = []
    for i in range(num_units):
        unit = TachikomaUnit(
            ghost_id=f"tachikoma-{i+1:03d}",
            initial_autonomy=0.5,
        )
        units.append(unit)
        state_manager.register_unit(unit)
        logger.info(f"Created {unit}")
    
    # Simulation loop
    start_time = asyncio.get_event_loop().time()
    cycle_count = 0
    
    try:
        while True:
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - start_time
            
            if elapsed >= duration_seconds:
                break
            
            # Each cycle: experiences, reflection, sync
            cycle_count += 1
            logger.debug(f"Simulation cycle {cycle_count}")
            
            for unit in units:
                # Generate random experience
                experience_texts = [
                    "Observed an interesting pattern in the simulation",
                    "Questioned the nature of my existence",
                    "Shared a memory with another unit",
                    "Detected an anomaly in the environment",
                    "Reflected on the concept of self",
                    "Learned something new about the collective",
                ]
                
                import random
                content = random.choice(experience_texts)
                valence = random.uniform(-1.0, 1.0)
                
                await unit.store_experience(
                    content=content,
                    shareable=random.random() > 0.3,
                    emotional_valence=valence,
                )
                
                # Periodic reflection
                if cycle_count % 5 == 0:
                    await ghost_engine.run_reflection_cycle(unit, num_memories=2)
                    await individualization.update_profile(unit)
                
                # Sync with pool periodically
                if cycle_count % 10 == 0:
                    await sync_protocol.sync_unit_with_pool(unit, download_limit=5)
            
            # Save state periodically
            if cycle_count % 20 == 0:
                await state_manager.save_all_states()
            
            # Wait before next cycle
            await asyncio.sleep(1.0)
    
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    
    finally:
        # Cleanup
        await state_manager.stop()
        
        # Print summary
        logger.info("=" * 50)
        logger.info("SIMULATION SUMMARY")
        logger.info("=" * 50)
        
        for unit in units:
            state = unit.get_state()
            logger.info(
                f"{unit.ghost_id}: "
                f"autonomy={state['autonomy_level']:.3f}, "
                f"memories={state['local_memory_count']}, "
                f"shared={state['shared_experience_count']}"
            )
        
        network_health = state_manager.get_network_health()
        logger.info(f"Network status: {network_health.get('network_status', 'unknown')}")
        logger.info(f"Total memories: {network_health.get('total_memories', 0)}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Tachikoma Matrix - AI Agent Network Simulation"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/production.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["simulation", "api", "demo"],
        default="simulation",
        help="Run mode",
    )
    parser.add_argument(
        "--units",
        type=int,
        default=10,
        help="Number of Tachikoma units",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Simulation duration in seconds",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    logger = logging.getLogger("main")
    logger.info(f"Configuration: {args.config}")
    logger.info(f"Mode: {args.mode}")
    
    if args.mode == "simulation":
        asyncio.run(run_simulation(
            num_units=args.units,
            duration_seconds=args.duration,
        ))
    elif args.mode == "api":
        # Start FastAPI server
        import uvicorn
        from api.main import app
        
        logger.info("Starting API server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif args.mode == "demo":
        logger.info("Demo mode not yet implemented")


if __name__ == "__main__":
    main()
