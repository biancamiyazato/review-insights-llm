# Formato da resposta que o Gemini deve devolver para cada avaliação
from enum import Enum

from pydantic import BaseModel, Field


class Sentimento(str, Enum):
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"


class Categoria(str, Enum):
    ATRASO = "atraso"
    NAO_ENTREGUE = "nao_entregue"
    DANIFICADO = "produto_danificado"
    ERRADO_INCOMPLETO = "produto_errado_ou_incompleto"
    QUALIDADE = "qualidade_do_produto"
    ATENDIMENTO = "atendimento"
    ELOGIO = "elogio"
    OUTRO = "outro"


class AnaliseAvaliacao(BaseModel):
    review_id: str = Field(description="O mesmo review_id recebido na entrada")
    sentimento: Sentimento
    categoria: Categoria = Field(description="O assunto principal da avaliação")
    resumo: str = Field(description="Resumo da avaliação em uma frase curta, em português")