# Etapa 6: demo online do analisador de avaliações
import json
import os
import sys
from pathlib import Path

import streamlit as st

# Permite importar os módulos da pasta src
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

# No Streamlit Cloud, a chave vem dos "Secrets"; no computador, do arquivo .env
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ.setdefault("GEMINI_API_KEY", st.secrets["GEMINI_API_KEY"])
except Exception:
    pass  # sem secrets.toml: usa o .env (rodando localmente)

from google.genai import errors, types  # noqa: E402

from config import MODEL, RESULTS_DIR  # noqa: E402
from llm import get_client  # noqa: E402
from prompts import SYSTEM_PROMPT  # noqa: E402
from schema import AnaliseAvaliacao  # noqa: E402

LIMITE_POR_SESSAO = 10   # análises por visitante, para não esgotar a cota gratuita
MAX_CARACTERES = 1000

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
EMOJI_SENTIMENTO = {"positivo": "🙂 Positivo", "neutro": "😐 Neutro", "negativo": "🙁 Negativo"}

EXEMPLOS = {
    "Escolha um exemplo...": "",
    "Não entregue": "Comprei há mais de um mês e até agora nada. Já passou do prazo e ninguém me dá retorno.",
    "Produto errado": "Pedi a cor preta e veio azul. Além disso, faltou um dos cabos que aparecia no anúncio.",
    "Elogio": "Chegou antes do prazo, bem embalado e funcionando perfeitamente. Recomendo!",
    "Defeito": "O produto chegou rápido, mas não liga de jeito nenhum. Já veio com defeito.",
}

st.set_page_config(page_title="Review Insights LLM", page_icon="💬", layout="centered")


@st.cache_resource
def cliente():
    return get_client()


def analisar(texto):
    """Envia uma avaliação ao Gemini e devolve a análise estruturada."""
    entrada = [{"review_id": "demo", "texto": texto}]
    resposta = cliente().models.generate_content(
        model=MODEL,
        contents=json.dumps(entrada, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=list[AnaliseAvaliacao],
            temperature=0,
        ),
    )
    if not resposta.parsed:
        raise ValueError("Resposta fora do formato esperado.")
    return resposta.parsed[0]


st.title("💬 Review Insights LLM")
st.write(
    "Analisador de avaliações de clientes com IA generativa (Gemini). "
    "Cole uma avaliação de compra online e veja o sentimento, a categoria do problema e um resumo."
)

aba_analisar, aba_resultados, aba_sobre = st.tabs(["Analisar", "Resultados do projeto", "Sobre"])

with aba_analisar:
    if "usos" not in st.session_state:
        st.session_state.usos = 0
    if "texto" not in st.session_state:
        st.session_state.texto = ""

    def usar_exemplo():
        st.session_state.texto = EXEMPLOS[st.session_state.exemplo]

    st.selectbox("Exemplos", list(EXEMPLOS), key="exemplo", on_change=usar_exemplo)
    texto = st.text_area(
        "Avaliação",
        key="texto",
        height=130,
        max_chars=MAX_CARACTERES,
        placeholder="Ex.: O produto chegou quebrado e a loja não responde meus e-mails.",
    )
    st.caption("Não escreva dados pessoais: o texto é enviado à API do Google Gemini.")

    restantes = LIMITE_POR_SESSAO - st.session_state.usos
    if st.button("Analisar", type="primary", disabled=restantes <= 0):
        if len(texto.strip()) < 10:
            st.warning("Escreva uma avaliação um pouco maior (pelo menos 10 caracteres).")
        else:
            with st.spinner("Analisando..."):
                try:
                    analise = analisar(texto.strip())
                    st.session_state.usos += 1
                    col1, col2 = st.columns(2)
                    col1.metric("Sentimento", EMOJI_SENTIMENTO[analise.sentimento.value])
                    col2.metric("Categoria", NOMES[analise.categoria.value])
                    st.info(f"**Resumo:** {analise.resumo}")
                except errors.APIError as erro:
                    if erro.code in (429, 503, 504):
                        st.error("O modelo está sobrecarregado ou o limite gratuito foi atingido. Tente de novo em alguns minutos.")
                    else:
                        st.error(f"Erro na API do Gemini (código {erro.code}).")
                except Exception:
                    st.error("Não foi possível analisar agora. Tente novamente.")
    if restantes <= 0:
        st.warning(f"Limite de {LIMITE_POR_SESSAO} análises por visita atingido.")
    else:
        st.caption(f"Análises restantes nesta visita: {restantes}")

with aba_resultados:
    arquivo_metricas = RESULTS_DIR / "metrics.json"
    if arquivo_metricas.exists():
        metricas = json.loads(arquivo_metricas.read_text(encoding="utf-8"))
        st.subheader("Qualidade do modelo")
        col1, col2 = st.columns(2)
        col1.metric(
            "Categoria x rótulos manuais",
            f"{metricas['categoria']['acuracia']:.1%}",
            help=f"Acurácia em {metricas['categoria']['n']} avaliações rotuladas à mão",
        )
        col2.metric(
            "Sentimento x estrelas",
            f"{metricas['sentimento']['acuracia']:.1%}",
            help=f"Acurácia em {metricas['sentimento']['n']} avaliações",
        )
        st.caption(f"Modelo: {metricas['modelo']}")
    st.subheader("Insights")
    for imagem in ["insight_problemas_negativas.png", "insight_nota_media.png"]:
        caminho = RESULTS_DIR / imagem
        if caminho.exists():
            st.image(str(caminho), width="stretch")

with aba_sobre:
    st.markdown(
        """
Projeto de portfólio que usa um LLM para transformar avaliações de clientes em dados estruturados
e mede a confiabilidade do resultado.

- **Dados:** 500 avaliações reais do dataset público da Olist (Kaggle)
- **Modelo:** Gemini, com saída estruturada em JSON validada por esquema (pydantic)
- **Avaliação:** comparação com 100 avaliações rotuladas manualmente e com as notas em estrelas

Código, metodologia e limitações: [github.com/biancamiyazato/review-insights-llm](https://github.com/biancamiyazato/review-insights-llm)

Desenvolvido por Bianca Miyazato · [LinkedIn](https://www.linkedin.com/in/biancamiyazato)
"""
    )