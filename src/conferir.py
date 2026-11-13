# Mostra avaliações lado a lado com a análise do modelo, para conferir à mão
import pandas as pd

from config import EXTRACTIONS_CSV, SAMPLE_CSV

amostra = pd.read_csv(SAMPLE_CSV)
analises = pd.read_csv(EXTRACTIONS_CSV)
juntos = amostra.merge(analises, on="review_id")

for linha in juntos.head(15).itertuples():
    print(f"[{linha.review_score} estrelas] {linha.review_comment_message}")
    print(f"  -> {linha.sentimento} | {linha.categoria} | {linha.resumo}\n")