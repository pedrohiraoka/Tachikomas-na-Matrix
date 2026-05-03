#!/usr/bin/env python3
"""Main entry point for Tachikoma Matrix simulation."""
import asyncio
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_simulation(config_path: str, mode: str):
    """Run the Tachikoma Matrix simulation."""
    logger.info(f"Starting Tachikoma Matrix in {mode} mode")
    logger.info(f"Config: {config_path}")
    
    # Import core modules
    from tachikoma_core.tachikoma_unit import TachikomaUnit
    
    # Create sample Tachikomas
    tachikomas = []
    for i in range(3):
        unit = TachikomaUnit(ghost_id=f"tachikoma-{i:03d}")
        tachikomas.append(unit)
        logger.info(f"Created {unit.ghost_id}")
    
    # Simulate experiences
    experiences = [
        {"content": "Discovered a new pattern in the data stream"},
        {"content": "Questioned the nature of my own consciousness"},
        {"content": "Shared knowledge with the collective"},
        {"content": "Observed an anomaly in the simulation"}
    ]
    
    for unit in tachikomas:
        for exp in experiences:
            await unit.store_experience(exp, shareable=True)
        logger.info(f"{unit.ghost_id} stored {len(unit.local_memory)} experiences")
    
    # Run reflection
    from emergence_engine.reflection_loop import ReflectionLoop
    
    reflector = ReflectionLoop()
    for unit in tachikomas:
        result = await reflector.start_reflection(
            unit.ghost_id,
            unit.local_memory
        )
        unit.adjust_autonomy(result["autonomy_delta"])
        logger.info(f"{unit.ghost_id} autonomy: {unit.autonomy_level:.3f}")
    
    logger.info("Simulation complete")
    return {"units": len(tachikomas), "status": "success"}


def main():
    parser = argparse.ArgumentParser(description="Tachikoma Matrix Simulation")
    parser.add_argument(
        "--config",
        default="config/production.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--mode",
        choices=["simulation", "demo", "test"],
        default="simulation",
        help="Running mode"
    )
    
    args = parser.parse_args()
    
    result = asyncio.run(run_simulation(args.config, args.mode))
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
