"""Test core modules."""
import pytest
import asyncio
from tachikoma_core import TachikomaUnit


def test_create_unit():
    """Test creating a Tachikoma unit."""
    unit = TachikomaUnit(ghost_id="test-001")
    assert unit.ghost_id == "test-001"
    assert 0.5 <= unit.autonomy_level <= 0.6


@pytest.mark.asyncio
async def test_store_experience():
    """Test storing experiences."""
    unit = TachikomaUnit(ghost_id="test-002")
    exp = {"content": "Test experience"}
    
    await unit.store_experience(exp, shareable=True)
    assert len(unit.local_memory) == 1
    assert unit.local_memory[0]["content"] == "Test experience"


@pytest.mark.asyncio  
async def test_reflection():
    """Test reflection loop."""
    from emergence_engine import ReflectionLoop
    
    unit = TachikomaUnit(ghost_id="test-003")
    await unit.store_experience({"content": "Thinking about existence"})
    
    reflector = ReflectionLoop()
    result = await reflector.start_reflection(unit.ghost_id, unit.local_memory)
    
    assert "insights" in result
    assert result["tachikoma_id"] == "test-003"
