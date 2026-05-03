# Setup completo
./scripts/setup.sh  # Instala dependências, baixa ConceptNet, inicia serviços

# Iniciar ambiente de desenvolvimento
docker-compose up -d  # Backend, Redis, PostgreSQL, Neo4j
cd frontend && npm run dev  # Frontend em hot-reload

# Executar demo guiada
python demos/collective_consciousness_demo.py  # Simula 10 Tachikomas aprendendo juntas
python demos/individuality_emergence_demo.py   # Foca em uma unidade desenvolvendo traços únicos

# Testes
pytest tests/  # Suite completa de testes unitários e de integração
python tests/stress_test_sync.py  # Teste de carga na sincronização de rede