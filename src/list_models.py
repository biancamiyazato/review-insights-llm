from llm import get_client

client = get_client()
for modelo in client.models.list():
    print(modelo.name)