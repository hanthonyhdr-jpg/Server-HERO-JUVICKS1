import sqlite3
import json

db_path = r"h:\JUVIX SERVER OPERACIONAL VERSAO FINAL - Copia\SISTEMA LIMPO - ESTAVEL\DATABASE\sistema_vendas.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- ÚLTIMOS 5 ORÇAMENTOS ---")
cursor.execute("SELECT id, itens_json FROM orcamentos ORDER BY data DESC LIMIT 5")
rows = cursor.fetchall()

for row in rows:
    print(f"\nID: {row[0]}")
    try:
        itens = json.loads(row[1])
        for i, item in enumerate(itens):
            print(f"  Item {i+1}: {item.get('produto')} | Un: {item.get('unidade')} | Dim: {item.get('dimensoes', 'NÃO TEM CHAVE DIM')} | Sub: {item.get('subtotal')}")
    except Exception as e:
        print(f"  Erro ao ler JSON: {e}")

conn.close()
