# Tachikoma Matrix - AI Agent Network Simulation

A full-stack Python application simulating a network of AI agents inspired by Tachikomas (Ghost in the Shell) operating within a Matrix-like simulated environment, integrated with ConceptNet for semantic knowledge.

## Features

- **Tachikoma Units**: Autonomous AI agents with unique identities, memory, and evolving personality vectors
- **Collective Memory**: Shared knowledge pool with Redis Pub/Sub synchronization
- **ConceptNet Integration**: Semantic reasoning using ConceptNet embeddings
- **Emergent Individuality**: Reflection loops that generate existential questions and update autonomy
- **Real-time Visualization**: WebSocket-based network monitoring

## Architecture

```
├── tachikoma_core/       # Core Tachikoma unit implementation
├── matrix_simulation/    # Simulated environment engine
├── knowledge_engine/     # ConceptNet integration
├── emergence_engine/     # Reflection and identity formation
├── api/                  # FastAPI REST + WebSocket API
├── frontend/             # React dashboard (to be implemented)
├── config/               # Configuration files
└── demos/                # Demo scripts
```

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- Node.js 18+ (for frontend)

### Installation

```bash
# Clone and setup
cd /workspace
pip install -r requirements.txt

# Download ConceptNet (optional, for full semantic features)
python scripts/download_conceptnet.py

# Run simulation
python main.py --mode simulation
```

### Docker Deployment

```bash
docker-compose up -d
```

Services available:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- Grafana: http://localhost:3001
- Neo4j Browser: http://localhost:7474

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tachikomas/{id}/experience` | Register experience |
| GET | `/api/v1/network/collective-memory?query=` | Search memories |
| POST | `/api/v1/tachikomas/{id}/reflect` | Trigger reflection |
| GET | `/api/v1/tachikomas/{id}/state` | Get unit state |
| WS | `/ws/network/realtime` | Real-time events |

## Example Usage

```python
from tachikoma_core import TachikomaUnit
from emergence_engine import ReflectionLoop

# Create unit
unit = TachikomaUnit(ghost_id="tachikoma-001")

# Store experiences
await unit.store_experience("Discovered pattern in data", shareable=True)
await unit.store_experience("Questioned my existence", shareable=False)

# Reflect
reflector = ReflectionLoop()
result = await reflector.start_reflection(unit.ghost_id, unit.local_memory)
print(f"Autonomy delta: {result['autonomy_delta']}")
```

## Configuration

Edit `config/ethics_config.yaml` for:
- Autonomy thresholds
- Sync policies
- Operator controls
- Bias detection settings

## Ethics Considerations

This is a conceptual experiment exploring:
- Emergent consciousness in AI systems
- Collective vs individual memory
- Autonomy and consent in networked agents

All Tachikoma units are simulations; no actual consciousness is created.

## License

MIT License - Educational/Research Purpose
