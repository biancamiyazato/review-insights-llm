# Etapa 4 (parte 2): mede o quanto o modelo acerta
import json

import matplotlib

matplotlib.use("Agg")  # gera as imagens sem abrir janelas
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
)

from config import EXTRACTIONS_CSV, MANUAL_XLSX, RESULTS_DIR, SAMPLE_CSV
from schema import Categoria, Sentimento

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

amostra = pd.read_csv(SAMPLE_CSV)
analises = pd.read_csv(EXTRACTIONS_CSV)
dados = amostra.merge(analises, on="review_id")


def salvar_matriz(reais, previstos, rotulos, titulo, arquivo):
    """Salva a matriz de confusão como imagem."""
    fig, ax = plt.subplots(figsize=(8, 7))
    ConfusionMatrixDisplay.from_predictions(
        reais, previstos, labels=rotulos, ax=ax, cmap="Blues", colorbar=False
    )
    ax.set_title(titulo)
    ax.set_xlabel("Previsto pelo modelo")
    ax.set_ylabel("Referência")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / arquivo, dpi=150)
    plt.close(fig)


# 1) Sentimento do modelo x nota em estrelas (500 avaliações)
def estrelas_para_sentimento(nota):
    if nota <= 2:
        return "negativo"
    if nota == 3:
        return "neutro"
    return "positivo"


dados["sentimento_estrelas"] = dados["review_score"].apply(estrelas_para_sentimento)
rotulos_sent = [s.value for s in Sentimento]
metricas_sent = {
    "n": len(dados),
    "acuracia": round(accuracy_score(dados["sentimento_estrelas"], dados["sentimento"]), 4),
    "f1_macro": round(
        f1_score(dados["sentimento_estrelas"], dados["sentimento"], labels=rotulos_sent,
                 average="macro", zero_division=0), 4
    ),
}
salvar_matriz(
    dados["sentimento_estrelas"], dados["sentimento"], rotulos_sent,
    "Sentimento: modelo x estrelas", "matriz_sentimento.png",
)

# 2) Categoria do modelo x rótulos manuais (100 avaliações)
manuais = pd.read_excel(MANUAL_XLSX, sheet_name="Rotulagem")
sem_rotulo = manuais["categoria_manual"].isna().sum()
if sem_rotulo:
    print(f"Atenção: {sem_rotulo} avaliação(ões) sem rótulo manual foram ignoradas.")
manuais = manuais.dropna(subset=["categoria_manual"])
cat = manuais[["review_id", "categoria_manual"]].merge(
    dados[["review_id", "review_score", "review_comment_message", "categoria", "resumo"]],
    on="review_id",
)
rotulos_cat = [c.value for c in Categoria]
presentes = [r for r in rotulos_cat if r in set(cat["categoria_manual"]) | set(cat["categoria"])]
metricas_cat = {
    "n": len(cat),
    "acuracia": round(accuracy_score(cat["categoria_manual"], cat["categoria"]), 4),
    "f1_macro": round(
        f1_score(cat["categoria_manual"], cat["categoria"], labels=presentes,
                 average="macro", zero_division=0), 4
    ),
    "por_categoria": classification_report(
        cat["categoria_manual"], cat["categoria"], labels=presentes,
        output_dict=True, zero_division=0,
    ),
}
salvar_matriz(
    cat["categoria_manual"], cat["categoria"], presentes,
    "Categoria: modelo x rótulo manual", "matriz_categoria.png",
)

# Discordâncias, para a análise de erros
erros = cat[cat["categoria_manual"] != cat["categoria"]]
erros.to_csv(RESULTS_DIR / "erros_categoria.csv", index=False)

# Resumo
modelo = analises["modelo"].iloc[0] if "modelo" in analises else "desconhecido"
resultado = {"modelo": modelo, "sentimento": metricas_sent, "categoria": metricas_cat}
with open(RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as arquivo:
    json.dump(resultado, arquivo, ensure_ascii=False, indent=2)

print(f"Modelo: {modelo}\n")
print(f"SENTIMENTO x estrelas ({metricas_sent['n']} avaliações)")
print(f"  acurácia: {metricas_sent['acuracia']:.1%} | F1 macro: {metricas_sent['f1_macro']:.3f}\n")
print(f"CATEGORIA x rótulo manual ({metricas_cat['n']} avaliações)")
print(f"  acurácia: {metricas_cat['acuracia']:.1%} | F1 macro: {metricas_cat['f1_macro']:.3f}")
print(f"  discordâncias: {len(erros)} (detalhes em results/erros_categoria.csv)\n")
print("Por categoria:")
print(classification_report(cat["categoria_manual"], cat["categoria"], labels=presentes, zero_division=0))
print(f"Arquivos salvos em {RESULTS_DIR}")