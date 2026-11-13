# Etapa 4 (parte 1): gera a planilha para rotular avaliações à mão
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from config import MANUAL_XLSX, N_ROTULOS, SAMPLE_CSV, SEED
from schema import Categoria

DEFINICOES = {
    "atraso": "O produto chegou, mas depois do prazo prometido.",
    "nao_entregue": "O cliente diz que não recebeu o produto.",
    "produto_danificado": "Chegou quebrado, amassado ou com defeito.",
    "produto_errado_ou_incompleto": "Chegou outro produto, cor/tamanho errado ou faltando itens.",
    "qualidade_do_produto": "Chegou certo, mas o cliente não gostou da qualidade.",
    "atendimento": "Problemas com a loja ou o vendedor (falta de resposta, troca, reembolso).",
    "elogio": "Avaliação positiva, sem problema relatado.",
    "outro": "Nenhuma das anteriores.",
}

# Protege os rótulos já feitos: não sobrescreve a planilha
if MANUAL_XLSX.exists():
    raise SystemExit(f"{MANUAL_XLSX} já existe. Apague o arquivo só se quiser gerar outro do zero.")

# Mesmo número de avaliações de cada nota, sem mostrar a nota (para não influenciar)
amostra = pd.read_csv(SAMPLE_CSV)
por_nota = N_ROTULOS // amostra["review_score"].nunique()
selecao = amostra.groupby("review_score").sample(n=por_nota, random_state=SEED)
selecao = selecao.sample(frac=1, random_state=SEED).reset_index(drop=True)

wb = Workbook()

# Aba 1: rotulagem
aba = wb.active
aba.title = "Rotulagem"
aba.append(["review_id", "avaliacao", "categoria_manual"])
for linha in selecao.itertuples():
    aba.append([linha.review_id, linha.review_comment_message, None])

for celula in aba[1]:
    celula.font = Font(bold=True)
    celula.fill = PatternFill("solid", fgColor="DDDDDD")
aba.column_dimensions["A"].hidden = True  # o id fica escondido, mas é usado depois
aba.column_dimensions["B"].width = 90
aba.column_dimensions["C"].width = 32
for linha in aba.iter_rows(min_row=2, min_col=2, max_col=2):
    linha[0].alignment = Alignment(wrap_text=True, vertical="top")
aba.freeze_panes = "B2"

# Lista suspensa só com as categorias válidas
categorias = [c.value for c in Categoria]
lista = DataValidation(type="list", formula1='"' + ",".join(categorias) + '"', allow_blank=True)
lista.error = "Escolha uma categoria da lista."
aba.add_data_validation(lista)
lista.add(f"C2:C{len(selecao) + 1}")

# Aba 2: definições das categorias, para consultar durante a rotulagem
ajuda = wb.create_sheet("Categorias")
ajuda.append(["categoria", "quando usar"])
for nome, definicao in DEFINICOES.items():
    ajuda.append([nome, definicao])
for celula in ajuda[1]:
    celula.font = Font(bold=True)
ajuda.column_dimensions["A"].width = 32
ajuda.column_dimensions["B"].width = 80

MANUAL_XLSX.parent.mkdir(parents=True, exist_ok=True)
wb.save(MANUAL_XLSX)
print(f"Planilha criada: {MANUAL_XLSX} ({len(selecao)} avaliações para rotular)")