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
│   ├── tachikoma_unit.py     # TachikomaUnit class with memory, personality, autonomy
│   ├── ghost_engine.py       # Consciousness engine with reflection cycles
│   ├── memory_sync.py        # Redis Pub/Sub synchronization
│   ├── individualization.py  # Divergence calculation and personality evolution
│   ├── network_protocol.py   # Message types and handlers
│   └── state_manager.py      # State snapshots and recovery
├── matrix_simulation/    # Simulated environment engine
│   ├── simulation_engine.py  # Event-based async simulation loop
│   ├── agent_programs.py     # Agent behavior patterns
│   ├── anomaly_detector.py   # Neo-like anomaly detection
│   ├── reality_layer.py      # Configurable reality rules
│   └── control_panel.py      # Simulation controls
├── knowledge_engine/     # ConceptNet integration
│   ├── conceptnet_loader.py  # Load ConceptNet embeddings
│   ├── graph_embedder.py     # Generate/manage embeddings
│   ├── semantic_reasoner.py  # Semantic inference
│   ├── memory_encoder.py     # Encode experiences to semantic memory
│   ├── query_interface.py    # Query interface for memories
│   └── concept_evolution.py  # Dynamic graph evolution
├── emergence_engine/     # Reflection and identity formation
│   ├── reflection_loop.py    # Async reflection with existential questions
│   ├── identity_formation.py # Identity and divergence tracking
│   ├── mortality_model.py    # Finitude modeling
│   ├── curiosity_generator.py# Exploration drive
│   ├── resistance_calculator.py # Command resistance based on autonomy
│   └── narrative_builder.py  # Personal/collective narratives
├── api/                  # FastAPI REST + WebSocket API
│   ├── main.py               # FastAPI app
│   ├── routes.py             # API endpoints
│   └── models.py             # Pydantic models
├── frontend/             # React + TypeScript dashboard
│   ├── src/components/       # NetworkView, MemoryExplorer, etc.
│   ├── src/store/            # Redux Toolkit slices
│   └── src/services/         # API and WebSocket clients
├── config/               # Configuration files
│   ├── ethics_config.yaml    # Ethical constraints
│   └── prometheus.yml        # Metrics configuration
├── demos/                # Demo scripts
│   ├── collective_consciousness_demo.py
│   └── individuality_emergence_demo.py
├── tests/                # pytest test suite
├── scripts/              # Utility scripts
│   └── preprocess_conceptnet.py
├── docker-compose.yml    # Docker orchestration
├── Dockerfile            # Backend container
├── setup.sh              # Setup script
└── main.py               # Entry point
```

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional, for full stack)
- Node.js 18+ (for frontend)

### Option 1: Using Setup Script (Recommended)

```bash
# Run complete setup
./setup.sh all

# Or run individual steps:
./setup.sh python      # Install Python dependencies
./setup.sh conceptnet  # Download ConceptNet embeddings
./setup.sh docker      # Start Docker services
./setup.sh test        # Run tests
```

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data/conceptnet data/embeddings logs

# Run simulation
python main.py --mode simulation
```

### Option 3: Docker Compose

```bash
# Start all services (backend, frontend, databases)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

After setup, access:
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:3000
- **Grafana Metrics**: http://localhost:3001 (admin/admin)
- **Neo4j Browser**: http://localhost:7474 (neo4j/neo4j_password)
- **Prometheus**: http://localhost:9090

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tachikomas/{id}/experience` | Register experience |
| GET | `/api/v1/network/collective-memory?query=` | Search memories |
| POST | `/api/v1/tachikomas/{id}/reflect` | Trigger reflection |
| GET | `/api/v1/tachikomas/{id}/state` | Get unit state |
| WS | `/ws/network/realtime` | Real-time events |

## Example Usage

### Python API

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

### REST API

```bash
# Register experience
curl -X POST http://localhost:8000/api/v1/tachikomas/tachikoma-001/experience \
  -H "Content-Type: application/json" \
  -d '{"content": "Exploring the matrix", "shareable": true}'

# Trigger reflection
curl -X POST http://localhost:8000/api/v1/tachikomas/tachikoma-001/reflect

# Get unit state
curl http://localhost:8000/api/v1/tachikomas/tachikoma-001/state

# Search collective memory
curl "http://localhost:8000/api/v1/network/collective-memory?query=consciousness&limit=10"
```

### Run Demos

```bash
# Collective consciousness demo (10 units learning together)
python demos/collective_consciousness_demo.py

# Individuality emergence demo (focus on one unit)
python demos/individuality_emergence_demo.py
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_core.py -v
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
