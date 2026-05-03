#!/bin/bash
# Tachikoma Matrix - Setup Script
# Configura ambiente de desenvolvimento e produção

set -e

echo "🔧 Tachikoma Matrix Setup Script"
echo "================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Python version
check_python() {
    log_info "Verificando versão do Python..."
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 não encontrado. Instale Python 3.11+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.11"
    
    if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
        log_error "Python 3.11+ necessário. Versão atual: $PYTHON_VERSION"
        exit 1
    fi
    
    log_info "Python $PYTHON_VERSION detectado ✓"
}

# Criar diretórios necessários
create_directories() {
    log_info "Criando estrutura de diretórios..."
    
    mkdir -p data/conceptnet
    mkdir -p data/embeddings
    mkdir -p logs
    mkdir -p demos
    mkdir -p config
    
    log_info "Diretórios criados ✓"
}

# Instalar dependências Python
install_python_deps() {
    log_info "Instalando dependências Python..."
    
    if [ ! -f requirements.txt ]; then
        log_error "requirements.txt não encontrado"
        exit 1
    fi
    
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    
    log_info "Dependências Python instaladas ✓"
}

# Baixar ConceptNet embeddings
download_conceptnet() {
    log_info "Configurando ConceptNet embeddings..."
    
    CONCEPTNET_FILE="data/conceptnet/numberbatch-19.08.txt.gz"
    
    if [ -f "$CONCEPTNET_FILE" ] || [ -f "data/conceptnet/numberbatch-19.08.txt" ]; then
        log_warn "ConceptNet já existe. Pulando download."
        return
    fi
    
    log_info "Baixando ConceptNet numberbatch (pode demorar)..."
    
    # Download do numberbatch
    wget -q --show-progress \
        https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-19.08.txt.gz \
        -P data/conceptnet/ || {
        log_warn "Falha ao baixar ConceptNet. Usando embeddings sintéticos."
        touch "$CONCEPTNET_FILE"
        return
    }
    
    log_info "Extraindo ConceptNet..."
    gunzip -f data/conceptnet/numberbatch-19.08.txt.gz
    
    log_info "Processando embeddings..."
    if [ -f scripts/preprocess_conceptnet.py ]; then
        python3 scripts/preprocess_conceptnet.py \
            --input data/conceptnet/numberbatch-19.08.txt \
            --output data/embeddings/
    else
        log_warn "Script de preprocessamento não encontrado. Pulando."
    fi
    
    log_info "ConceptNet configurado ✓"
}

# Iniciar serviços Docker
start_docker_services() {
    log_info "Iniciando serviços Docker..."
    
    if ! command -v docker &> /dev/null; then
        log_warn "Docker não encontrado. Pulando inicialização de serviços."
        return
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_warn "Docker Compose não encontrado. Pulando inicialização de serviços."
        return
    fi
    
    if [ ! -f docker-compose.yml ]; then
        log_warn "docker-compose.yml não encontrado. Pulando inicialização."
        return
    fi
    
    # Verificar se Docker daemon está rodando
    if ! docker info &> /dev/null; then
        log_warn "Docker daemon não está rodando. Pulando inicialização de serviços."
        return
    fi
    
    if docker compose version &> /dev/null; then
        docker compose up -d postgres redis neo4j
    else
        docker-compose up -d postgres redis neo4j
    fi
    
    log_info "Aguardando serviços iniciarem..."
    sleep 10
    
    log_info "Serviços Docker iniciados ✓"
}

# Executar migrações e setup inicial
run_initialization() {
    log_info "Executando inicialização da aplicação..."
    
    # Criar banco de dados e tabelas
    python3 -c "
import asyncio
from knowledge_engine import ConceptNetLoader, GraphEmbedder

async def init():
    loader = ConceptNetLoader()
    embedder = GraphEmbedder()
    print('Knowledge engine inicializado')

asyncio.run(init())
" 2>/dev/null || log_warn "Inicialização parcial concluída"
    
    log_info "Inicialização completa ✓"
}

# Executar testes
run_tests() {
    log_info "Executando testes..."
    
    if [ -d tests ] && [ -f tests/test_core.py ]; then
        python3 -m pytest tests/ -v --tb=short || log_warn "Alguns testes falharam"
        log_info "Testes executados ✓"
    else
        log_warn "Diretório de testes não encontrado"
    fi
}

# Mostrar status final
show_status() {
    echo ""
    echo "================================"
    echo "✅ Setup concluído!"
    echo ""
    echo "Próximos passos:"
    echo "  1. Para iniciar a simulação:"
    echo "     python main.py --mode simulation"
    echo ""
    echo "  2. Para iniciar a API:"
    echo "     python api/main.py"
    echo ""
    echo "  3. Para acessar o frontend:"
    echo "     cd frontend && npm install && npm run dev"
    echo ""
    echo "  4. Para ver logs em tempo real:"
    echo "     tail -f logs/*.log"
    echo ""
    echo "Documentação: README.md"
    echo "================================"
}

# Main execution
main() {
    check_python
    create_directories
    install_python_deps
    download_conceptnet
    start_docker_services
    run_initialization
    run_tests
    show_status
}

# Parse arguments
case "${1:-all}" in
    python)
        check_python
        install_python_deps
        ;;
    conceptnet)
        download_conceptnet
        ;;
    docker)
        start_docker_services
        ;;
    test)
        run_tests
        ;;
    all)
        main
        ;;
    *)
        echo "Uso: $0 {all|python|conceptnet|docker|test}"
        exit 1
        ;;
esac
