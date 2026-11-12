# Etapa 1: testa a conexão com o Gemini
from config import MODEL
from llm import get_client

client = get_client()
resposta = client.models.generate_content(
    model=MODEL,
    contents="Em uma frase, o que é análise de sentimentos?",
)
print(resposta.text)