import os
import sys
import json

# Adiciona o diretório PY ao path para importar database.py
sys.path.append(os.path.join(os.getcwd(), 'PY'))

from database import buscar_dados

print("--- ÚLTIMOS 5 ORÇAMENTOS (POSTGRES) ---")
try:
    df = buscar_dados("SELECT id, itens_json FROM orcamentos ORDER BY data DESC LIMIT 5")
    if df.empty:
        print("Nenhum orçamento encontrado no banco.")
    else:
        for _, row in df.iterrows():
            print(f"\nID: {row['id']}")
            try:
                itens = json.loads(row['itens_json'])
                for i, item in enumerate(itens):
                    dim = item.get('dimensoes', 'NÃO TEM CHAVE DIM')
                    un = item.get('unidade', 'un')
                    print(f"  Item {i+1}: {item.get('produto')} | Un: {un} | Dim: {dim}")
            except Exception as e:
                print(f"  Erro ao ler JSON: {e}")
except Exception as e:
    print(f"Erro ao conectar: {e}")
