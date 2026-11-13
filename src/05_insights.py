# Etapa 5: transforma as análises do modelo em insights e gráficos
import matplotlib

matplotlib.use("Agg")  # gera as imagens sem abrir janelas
import matplotlib.pyplot as plt
import pandas as pd

from config import EXTRACTIONS_CSV, RAW_CSV, RESULTS_DIR, SAMPLE_CSV

COR = "#2a78d6"            # cor única das barras
TEXTO = "#0b0b0b"          # texto principal
TEXTO_SECUNDARIO = "#52514e"
FUNDO = "#fcfcfb"

NOMES = {
    "atraso": "Atraso",
    "nao_entregue": "Não entregue",
    "produto_danificado": "Produto danificado",
    "produto_errado_ou_incompleto": "Produto errado ou incompleto",
    "qualidade_do_produto": "Qualidade do produto",
    "atendimento": "Atendimento",
    "elogio": "Elogio",
    "outro": "Outro",
}

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

amostra = pd.read_csv(SAMPLE_CSV)
analises = pd.read_csv(EXTRACTIONS_CSV)
dados = amostra.merge(analises, on="review_id")
dados["categoria_nome"] = dados["categoria"].map(NOMES)

# A amostra tem 100 avaliações de cada nota, mas no dataset real há muito mais
# avaliações de 5 estrelas do que de 2. Para os números representarem o dataset real,
# cada avaliação recebe um peso: (avaliações com comentário dessa nota) / (100 da amostra).
completo = pd.read_csv(RAW_CSV).dropna(subset=["review_comment_message"])
completo["review_comment_message"] = (
    completo["review_comment_message"].str.replace(r"\s+", " ", regex=True).str.strip()
)
completo = completo[completo["review_comment_message"].str.len() >= 10]
completo = completo.drop_duplicates(subset="review_id")
total_por_nota = completo["review_score"].value_counts()
amostra_por_nota = dados["review_score"].value_counts()
dados["peso"] = dados["review_score"].map(total_por_nota / amostra_por_nota)


def estilo(ax, titulo, subtitulo):
    """Visual limpo: sem moldura, grade discreta, títulos à esquerda."""
    ax.set_facecolor(FUNDO)
    ax.figure.set_facecolor(FUNDO)
    for lado in ["top", "right", "left"]:
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#d0cfca")
    ax.tick_params(colors=TEXTO_SECUNDARIO, length=0)
    ax.xaxis.grid(True, color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.figure.text(0.02, 0.96, titulo, fontsize=14, weight="bold", color=TEXTO, ha="left")
    ax.figure.text(0.02, 0.905, subtitulo, fontsize=10, color=TEXTO_SECUNDARIO, ha="left")


def barras(serie, titulo, subtitulo, rotulo_x, formato, arquivo, limite_x=None):
    """Barras horizontais ordenadas, com o valor escrito ao lado de cada barra."""
    serie = serie.sort_values()
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(serie) + 1.6))
    ax.barh(serie.index, serie.values, color=COR, height=0.6)
    for posicao, valor in enumerate(serie.values):
        ax.text(valor, posicao, "  " + formato(valor), va="center", color=TEXTO, fontsize=10)
    ax.set_xlabel(rotulo_x, color=TEXTO_SECUNDARIO)
    ax.set_xlim(0, limite_x or serie.max() * 1.18)
    ax.tick_params(axis="y", labelcolor=TEXTO, labelsize=10)
    estilo(ax, titulo, subtitulo)
    fig.subplots_adjust(left=0.35, right=0.95, top=0.84, bottom=0.12)
    fig.savefig(RESULTS_DIR / arquivo, dpi=150)
    plt.close(fig)


# Insight 1: quais problemas aparecem nas avaliações negativas (1 e 2 estrelas)
negativas = dados[dados["review_score"] <= 2]
problemas = negativas.groupby("categoria_nome")["peso"].sum()
problemas = problemas / problemas.sum() * 100
barras(
    problemas,
    "O que gera avaliações negativas",
    "Categoria identificada pelo LLM nas avaliações de 1 e 2 estrelas (% ponderado pelo dataset real)",
    "% das avaliações negativas",
    lambda v: f"{v:.0f}%",
    "insight_problemas_negativas.png",
)

# Insight 2: nota média de cada categoria (quais problemas deixam o cliente mais insatisfeito)
media = dados.groupby("categoria_nome").apply(
    lambda g: (g["review_score"] * g["peso"]).sum() / g["peso"].sum(), include_groups=False
)
contagem = dados["categoria_nome"].value_counts()
media.index = [f"{nome} (n={contagem[nome]})" for nome in media.index]
barras(
    media,
    "Nota média por categoria",
    "Média de estrelas das avaliações em cada categoria (ponderada pelo dataset real)",
    "Nota média (1 a 5 estrelas)",
    lambda v: f"{v:.1f}",
    "insight_nota_media.png",
    limite_x=5.6,
)

# Exemplos de resumos gerados pelo modelo, para o README
exemplos = (
    dados[dados["categoria"] != "elogio"]
    .groupby("categoria")
    .head(1)
    .head(5)
)
with open(RESULTS_DIR / "exemplos_resumos.md", "w", encoding="utf-8") as arquivo:
    arquivo.write("| Avaliação original | Categoria | Resumo do modelo |\n|---|---|---|\n")
    for linha in exemplos.itertuples():
        texto = linha.review_comment_message.replace("|", "/")
        arquivo.write(f"| {texto} | {linha.categoria} | {linha.resumo} |\n")

# Conclusões em texto
principal = problemas.idxmax()
print("INSIGHTS\n")
print("Avaliações negativas (1 e 2 estrelas), ponderado pelo dataset real:")
for nome, valor in problemas.sort_values(ascending=False).items():
    print(f"  {nome}: {valor:.1f}%")
print(f"\n-> O problema mais frequente nas avaliações negativas é '{principal}' ({problemas.max():.0f}%).\n")
print("Nota média por categoria:")
for nome, valor in media.sort_values().items():
    print(f"  {nome}: {valor:.2f}")
print(f"\nArquivos salvos em {RESULTS_DIR}")