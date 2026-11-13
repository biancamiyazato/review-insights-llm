# Configurações compartilhadas do projeto
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # pasta raiz do projeto

# MODEL = "gemini-3.8-flash"
# MODEL = "gemini-3.7-flash"

MODEL = "gemini-3.1-flash-lite"

# Dados
RAW_CSV = ROOT / "data" / "raw" / "olist_order_reviews_dataset.csv"
SAMPLE_CSV = ROOT / "data" / "processed" / "sample.csv"
SAMPLE_PER_SCORE = 100  # avaliações por nota (1 a 5 estrelas) -> 500 no total
SEED = 42               # semente fixa para reprodutibilidade

# Extração (Etapa 3)
EXTRACTIONS_CSV = ROOT / "data" / "processed" / "extractions.csv"
BATCH_SIZE = 20          # avaliações enviadas por pedido à API
PAUSA_ENTRE_LOTES = 5    # segundos de espera entre pedidos (limite do plano gratuito)
MAX_TENTATIVAS = 5       # tentativas por lote quando a API falha
LIMITE = None              # None = processa tudo; um número = processa só essa quantidade (teste)