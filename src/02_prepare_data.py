# Etapa 2: monta uma amostra equilibrada de avaliações com comentário
import pandas as pd

from config import RAW_CSV, SAMPLE_CSV, SAMPLE_PER_SCORE, SEED

df = pd.read_csv(RAW_CSV)
print(f"Avaliações no dataset: {len(df)}")

# Mantém só as avaliações com comentário escrito
df = df.dropna(subset=["review_comment_message"])
df["review_comment_message"] = (
    df["review_comment_message"].str.replace(r"\s+", " ", regex=True).str.strip()
)
df = df[df["review_comment_message"].str.len() >= 10]  # descarta comentários muito curtos
df = df.drop_duplicates(subset="review_id")
print(f"Avaliações com comentário: {len(df)}")
print(df["review_score"].value_counts().sort_index())

# Sorteia o mesmo número de avaliações para cada nota
amostra = df.groupby("review_score").sample(n=SAMPLE_PER_SCORE, random_state=SEED)
amostra = amostra[["review_id", "review_score", "review_comment_message"]]
amostra = amostra.sample(frac=1, random_state=SEED).reset_index(drop=True)  # embaralha

SAMPLE_CSV.parent.mkdir(parents=True, exist_ok=True)
amostra.to_csv(SAMPLE_CSV, index=False)
print(f"Amostra salva em {SAMPLE_CSV} ({len(amostra)} avaliações)")