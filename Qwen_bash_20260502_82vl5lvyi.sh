# Download e preparação dos dados
mkdir -p data/conceptnet
wget https://conceptnet.s3.amazonaws.com/downloads/2019/numberbatch/numberbatch-19.08.txt.gz -P data/conceptnet/
gunzip data/conceptnet/numberbatch-19.08.txt.gz

# Pré-processamento para Neo4j ou armazenamento vetorial
python scripts/preprocess_conceptnet.py --input data/conceptnet/numberbatch-19.08.txt --output data/embeddings/