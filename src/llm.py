# Conexão com a API do Gemini
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()  # lê o arquivo .env

from google.genai import types  # adicione esta linha junto com os outros imports


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY não encontrada. Confira o arquivo .env.")
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),  # 60 segundos (em milissegundos)
    )