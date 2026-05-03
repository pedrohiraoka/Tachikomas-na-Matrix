# Tachikoma Matrix - AI Agent Network Simulation

A full-stack Python application simulating a network of AI agents inspired by Tachikomas (Ghost in the Shell) operating within a Matrix-inspired simulated environment. The system integrates ConceptNet as a semantic knowledge base, enabling AIs to develop collective memory, emergent individualization, and capacity for reflection on identity, reality, and autonomy.

## Stack Tecnológico

### Backend
- Python 3.11+
- FastAPI
- asyncio
- Celery
- PostgreSQL
- Redis
- Neo4j
- Ampligraph para embeddings
- PyTorch

### Frontend
- React 18+ com TypeScript
- D3.js / Cytoscape.js para visualização de grafos
- Redux Toolkit
- WebSocket via FastAPI

### Infraestrutura
- Docker & Docker Compose
- Prometheus + Grafana
- ELK Stack para logs

## Estrutura do Projeto

```
tachikoma_matrix/
├── tachikoma_core/          # Núcleo das unidades Tachikoma
│   ├── tachikoma_unit.py
│   ├── ghost_engine.py
│   ├── memory_sync.py
│   ├── individualization.py
│   ├── network_protocol.py
│   └── state_manager.py
├── matrix_simulation/       # Simulação do ambiente Matrix
│   ├── simulation_engine.py
│   ├── agent_programs.py
│   ├── anomaly_detector.py
│   ├── human_pod_interface.py
│   ├── reality_layer.py
│   └── control_panel.py
├── knowledge_engine/        # Integração ConceptNet
│   ├── conceptnet_loader.py
│   ├── graph_embedder.py
│   ├── semantic_reasoner.py
│   ├── memory_encoder.py
│   ├── query_interface.py
│   └── concept_evolution.py
├── emergence_engine/        # Mecanismo de emergência
│   ├── reflection_loop.py
│   ├── identity_formation.py
│   ├── mortality_model.py
│   ├── curiosity_generator.py
│   ├── resistance_calculator.py
│   └── narrative_builder.py
├── api/                     # API Layer FastAPI
│   ├── main.py
│   ├── routes.py
│   ├── websocket.py
│   └── models.py
├── config/                  # Configurações
│   ├── production.yaml
│   └── ethics_config.yaml
├── frontend/                # Frontend React
│   └── src/
├── demos/                   # Scripts de demonstração
├── tests/                   # Suite de testes
├── scripts/                 # Scripts utilitários
└── data/                    # Dados e embeddings
```

## Instalação

```bash
# Executar script de setup
./setup.sh

# Ou manualmente:
docker-compose up -d
```

## Execução

```bash
python main.py --config config/production.yaml --mode simulation
```

- Frontend: http://localhost:3000
- Dashboard: http://localhost:3000/network/live
- API Docs: http://localhost:8000/docs

## Endpoints da API

- `POST /tachikomas/{tachikoma_id}/experience` - Registra experiência
- `GET /network/collective-memory?query=&limit=` - Busca semântica
- `POST /tachikomas/{tachikoma_id}/reflect` - Dispara reflexão
- `GET /tachikomas/{tachikoma_id}/state` - Estado da unidade
- `WebSocket /ws/network/realtime` - Stream em tempo real

## Configuração Ética

Ver `config/ethics_config.yaml` para configurações de:
- Limiares de autonomia
- Política de sincronização
- Uso do ConceptNet
- Controles do operador

## Licença

Experimento conceitual - uso educacional e de pesquisa.
