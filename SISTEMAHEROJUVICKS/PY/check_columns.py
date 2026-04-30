import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'PY'))
from database import buscar_dados

print("--- COLUNAS DA TABELA ORCAMENTOS ---")
try:
    df = buscar_dados("SELECT * FROM orcamentos LIMIT 1")
    print(df.columns.tolist())
except Exception as e:
    print(f"Erro: {e}")
