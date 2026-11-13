# Instruções enviadas ao Gemini na Etapa 3
SYSTEM_PROMPT = """Você analisa avaliações de clientes de uma loja online brasileira.

Você vai receber uma lista em JSON. Cada item tem um "review_id" e o "texto" da avaliação.
Para CADA item, devolva o mesmo review_id e:

1. sentimento: "positivo", "neutro" ou "negativo".
2. categoria: o assunto PRINCIPAL da avaliação, escolhendo uma destas:
   - atraso: o produto chegou, mas depois do prazo prometido.
   - nao_entregue: o cliente diz que não recebeu o produto.
   - produto_danificado: chegou quebrado, amassado ou com defeito.
   - produto_errado_ou_incompleto: chegou outro produto, cor/tamanho errado ou faltando itens.
   - qualidade_do_produto: o produto chegou certo, mas o cliente não gostou da qualidade.
   - atendimento: problemas com a loja ou o vendedor (falta de resposta, troca, reembolso).
   - elogio: avaliação positiva, sem problema relatado.
   - outro: nenhuma das anteriores.
3. resumo: uma frase curta, em português, com o essencial da avaliação.

Regras:
- Se houver mais de um problema, escolha o que o cliente mais enfatiza.
- Elogio com ressalva leve (ex.: "chegou rápido, mas a caixa veio amassada") tem sentimento "neutro" e a categoria do problema.
- Responda todos os itens recebidos, na mesma ordem.

Exemplos:
- "Ainda não recebi meu pedido e já passou do prazo." -> negativo, nao_entregue
- "Chegou antes do prazo, produto ótimo, recomendo!" -> positivo, elogio
- "Pedi duas unidades e só veio uma." -> negativo, produto_errado_ou_incompleto
"""