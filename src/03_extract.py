# Etapa 3: usa o Gemini para extrair sentimento, categoria e resumo de cada avaliação
import json
import time

import pandas as pd
from google.genai import errors, types

from config import (
    BATCH_SIZE,
    EXTRACTIONS_CSV,
    LIMITE,
    MAX_TENTATIVAS,
    MODEL,
    PAUSA_ENTRE_LOTES,
    SAMPLE_CSV,
)
from llm import get_client
from prompts import SYSTEM_PROMPT
from schema import AnaliseAvaliacao

ERROS_TEMPORARIOS = {429, 500, 503, 504}  # vale a pena esperar e tentar de novo

CONFIG_GERACAO = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    response_mime_type="application/json",
    response_schema=list[AnaliseAvaliacao],
    temperature=0,  # respostas mais estáveis entre execuções
)


def analisar_lote(client, lote):
    """Envia um lote de avaliações e devolve a lista de análises."""
    # A nota em estrelas NÃO é enviada: ela é usada só na avaliação (Etapa 4)
    entrada = [
        {"review_id": linha.review_id, "texto": linha.review_comment_message}
        for linha in lote.itertuples()
    ]
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resposta = client.models.generate_content(
                model=MODEL,
                contents=json.dumps(entrada, ensure_ascii=False),
                config=CONFIG_GERACAO,
            )
            if resposta.parsed is not None:
                return resposta.parsed
            print(f"  resposta fora do formato (tentativa {tentativa})")
        except errors.APIError as erro:
            if erro.code not in ERROS_TEMPORARIOS:
                raise  # erro de chave, de pedido etc.: não adianta repetir
            print(f"  erro {erro.code} (tentativa {tentativa})")
        espera = 10 * 2 ** (tentativa - 1)  # 10s, 20s, 40s, 80s...
        print(f"  tentando de novo em {espera}s...")
        time.sleep(espera)
    raise RuntimeError(f"O lote falhou {MAX_TENTATIVAS} vezes seguidas. Tente mais tarde.")


def main():
    client = get_client()
    amostra = pd.read_csv(SAMPLE_CSV)

    # Retoma de onde parou: pula as avaliações já analisadas
    if EXTRACTIONS_CSV.exists():
        ja_feitas = set(pd.read_csv(EXTRACTIONS_CSV)["review_id"])
    else:
        ja_feitas = set()
    pendentes = amostra[~amostra["review_id"].isin(ja_feitas)]
    if LIMITE is not None:
        pendentes = pendentes.head(max(LIMITE - len(ja_feitas), 0))

    print(f"Modelo: {MODEL}")
    print(f"Já analisadas: {len(ja_feitas)} | A analisar agora: {len(pendentes)}")

    for inicio in range(0, len(pendentes), BATCH_SIZE):
        lote = pendentes.iloc[inicio : inicio + BATCH_SIZE]
        print(f"Lote {inicio // BATCH_SIZE + 1}: {len(lote)} avaliações")

        analises = analisar_lote(client, lote)

        # Guarda só as respostas cujo review_id veio de fato no lote
        ids_do_lote = set(lote["review_id"])
        linhas = [a.model_dump(mode="json") for a in analises if a.review_id in ids_do_lote]
        faltando = len(ids_do_lote) - len({linha["review_id"] for linha in linhas})
        if faltando:
            print(f"  {faltando} avaliação(ões) sem resposta; serão refeitas na próxima execução")

        if not linhas:
            continue

        resultado = pd.DataFrame(linhas).drop_duplicates(subset="review_id")
        resultado["modelo"] = MODEL
        resultado.to_csv(
            EXTRACTIONS_CSV,
            mode="a",
            header=not EXTRACTIONS_CSV.exists(),
            index=False,
        )
        time.sleep(PAUSA_ENTRE_LOTES)

    total = len(pd.read_csv(EXTRACTIONS_CSV)) if EXTRACTIONS_CSV.exists() else 0
    print(f"Concluído. Total analisado: {total} de {len(amostra)}")


if __name__ == "__main__":
    main()