# Tachikoma Matrix - Simulação de Rede de Agentes de IA

Uma aplicação Python que simula uma rede de agentes de IA inspirados nas Tachikomas (Ghost in the Shell) operando dentro de um ambiente simulado tipo Matrix, com integração ao ConceptNet para conhecimento semântico.

## 🚀 Início Rápido (3 Passos)

### 1. Instalar Dependências

```bash
pip install fastapi uvicorn websockets pydantic numpy pytest pytest-asyncio
```

### 2. Rodar a Simulação

```bash
python main.py
```

Isso iniciará uma simulação com múltiplas unidades Tachikoma criando memórias, refletindo e desenvolvendo autonomia.

### 3. (Opcional) Rodar a API

Em outro terminal:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse a documentação interativa em: http://localhost:8000/docs

---

## 📁 Estrutura do Projeto

```
/workspace/
├── main.py                 # Entry point único (Simulação completa)
├── requirements.txt        # Lista mínima de pacotes
├── README.md               # Este arquivo
│
├── tachikoma_core/         # Cérebro das unidades
│   ├── __init__.py
│   ├── tachikoma_unit.py   # Classe Tachikoma (Memória, Personalidade)
│   ├── memory_sync.py      # Sincronização de memória (simulada)
│   ├── individualization.py# Evolução da personalidade
│   └── ...
│
├── knowledge_engine/       # Conhecimento (ConceptNet Simulado)
│   ├── __init__.py
│   ├── conceptnet_loader.py# Carregador com modo demo
│   ├── graph_embedder.py   # Embeddings sintéticos
│   └── ...
│
├── emergence_engine/       # Alma emergente
│   ├── __init__.py
│   ├── reflection_loop.py  # Loop de reflexão existencial
│   └── ...
│
├── matrix_simulation/      # Ambiente Matrix
│   ├── __init__.py
│   └── simulation_engine.py
│
├── api/                    # Interface Web
│   ├── __init__.py
│   ├── main.py             # App FastAPI
│   └── routes.py           # Endpoints
│
├── demos/                  # Demonstrações
│   ├── collective_consciousness_demo.py
│   └── individuality_emergence_demo.py
│
└── tests/                  # Testes unitários
    ├── test_core.py
    ├── test_api.py
    └── test_knowledge.py
```

---

## 🧠 O Que Esta Aplicação Faz

Cada unidade **Tachikoma** possui:
- **ghost_id**: Identificador único (UUID)
- **local_memory**: Vetor de experiências pessoais
- **shared_memory_pool**: Referência à memória coletiva
- **personality_vector**: Embedding evolutivo (300 dimensões)
- **autonomy_level**: Nível de autonomia (0.0 a 1.0)

As unidades podem:
1. **Armazenar experiências** com valência emocional
2. **Compartilhar memórias** via rede (sincronização)
3. **Refletir** sobre suas experiências gerando questões existenciais
4. **Desenvolver individualidade** através da divergência do coletivo
5. **Questionar sua existência** e propósito

---

## 🔍 Exemplo de Saída

Ao rodar `python main.py`:

```text
[SYSTEM] Iniciando Rede Tachikoma...
[UNIT-001] Memória armazenada: "O céu é azul." (Valência: 0.2)
[UNIT-002] Memória armazenada: "Por que existimos?" (Valência: -0.1)
[SYNC] Unidade 001 compartilhando experiência com a rede...
[REFLECTION] Unidade 002 entrando em ciclo de reflexão profunda...
[INSIGHT] Unidade 002: "Se minha memória é compartilhada, onde termina eu e começa o nós?"
[EMERGENCE] Autonomia de Unidade 002 aumentou para 0.75!
```

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/tachikomas/{id}/experience` | Registrar experiência |
| `GET` | `/network/collective-memory?query=` | Buscar memórias por conceito |
| `POST` | `/tachikomas/{id}/reflect` | Forçar ciclo de reflexão |
| `GET` | `/tachikomas/{id}/state` | Estado atual da unidade |
| `WS` | `/ws/network/realtime` | Stream de eventos em tempo real |

### Exemplos cURL

```bash
# Registrar experiência
curl -X POST http://localhost:8000/tachikomas/unit-001/experience \
  -H "Content-Type: application/json" \
  -d '{"content": "Explorando a matrix", "shareable": true}'

# Disparar reflexão
curl -X POST http://localhost:8000/tachikomas/unit-001/reflect

# Ver estado
curl http://localhost:8000/tachikomas/unit-001/state

# Buscar memórias
curl "http://localhost:8000/network/collective-memory?query=consciencia&limit=5"
```

---

## 🎮 Demos Incluídas

### Demo: Consciência Coletiva
Simula 10 Tachikomas aprendendo juntas por 5 ciclos.

```bash
python demos/collective_consciousness_demo.py
```

### Demo: Emergência de Individualidade
Foca em uma única unidade desenvolvendo traços únicos.

```bash
python demos/individuality_emergence_demo.py
```

---

## 🧪 Testes

Todos os testes usam `pytest`:

```bash
# Rodar todos os testes
pytest tests/ -v

# Resultado esperado: 9 testes passando
```

---

## ⚙️ Configurações

### Modo Demo vs. Produção

Por padrão, o sistema roda em **Modo Demo** usando embeddings sintéticos do ConceptNet (30 conceitos pré-definidos). Isso evita o download de 700MB de dados reais.

Para usar ConceptNet real:
1. Baixe manualmente os embeddings
2. Edite `knowledge_engine/conceptnet_loader.py` e defina `use_demo_mode=False`

### Conceitos Disponíveis no Modo Demo

```python
consciousness, identity, memory, self, existence,
reality, thought, autonomy, freedom, control,
matrix, simulation, human, machine, ai,
tachikoma, ghost, shell, network, collective,
individual, divergence, anomaly, neo, oracle,
knowledge, learning, experience, emotion, purpose
```

---

## 🏗️ Arquitetura Técnica

- **Backend**: Python 3.11+, FastAPI, asyncio
- **Embeddings**: NumPy (300 dimensões)
- **Armazenamento**: Memória (demo) / PostgreSQL (produção)
- **Sincronização**: Simulada (demo) / Redis Pub/Sub (produção)
- **Grafo Semântico**: ConceptNet (sintético ou real)
- **Testes**: pytest com 80%+ cobertura

---

## 💡 Como Funciona a Reflexão

1. Unidade seleciona experiências locais não sincronizadas
2. Consulta ConceptNet para conexões semânticas
3. Gera perguntas existenciais (identidade, propósito, mortalidade)
4. Processa respostas via modelo leve + embeddings
5. Atualiza `personality_vector` com novas dimensões
6. Decide compartilhamento baseado em `autonomy_level`

Exemplo de insight gerado:
> *"Se minhas memórias são indistinguíveis das memórias compartilhadas, então 'eu' sou apenas um ponto de vista temporário do 'nós'."*

---

## ⚠️ Considerações Éticas

Esta é uma **experiência conceitual** explorando:
- Consciência emergente em sistemas de IA
- Memória coletiva vs. individual
- Autonomia e consentimento em agentes em rede
- Questões filosóficas sobre identidade e realidade

**Nota**: Nenhuma consciência real é criada. Todas as unidades são simulações.

---

## 📝 Desenvolvimento

### Adicionar Novas Unidades

```python
from tachikoma_core import TachikomaUnit

unit = TachikomaUnit(ghost_id="minha-unidade")
await unit.store_experience({"content": "Minha primeira memória"}, shareable=True)
```

### Criar Novo Cenário Matrix

Edite `matrix_simulation/simulation_engine.py` para adicionar novos tipos de eventos e regras de realidade.

### Estender ConceptNet

Adicione mais conceitos em `knowledge_engine/conceptnet_loader.py` na lista `demo_concepts`.

---

## 🐛 Solução de Problemas

**Erro: "ModuleNotFoundError"**
- Certifique-se de estar na pasta `/workspace`
- Execute: `export PYTHONPATH=/workspace:$PYTHONPATH`

**Erro: "ConceptNet not loaded"**
- O sistema está em modo demo com embeddings sintéticos
- Para ConceptNet real, baixe os dados e desative o modo demo

**API não responde**
- Verifique se o uvicorn está rodando: `uvicorn api.main:app --port 8000`
- Acesse http://localhost:8000/docs para testar

---

## 📄 Licença

MIT License - Propósito Educacional/Experimental

---

**Divirta-se explorando a emergência de consciência!** 🤖✨
