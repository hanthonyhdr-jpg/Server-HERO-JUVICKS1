import sqlite3
import json
import os

db_path = r'h:\renova\sistema_vendas.db'

def check_json():
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, itens_json, fotos_json FROM orcamentos")
        rows = cursor.fetchall()
        
        print(f"Checking {len(rows)} records...")
        
        for row_id, itens, fotos in rows:
            # Check itens_json
            if itens and itens.strip():
                try:
                    json.loads(itens)
                except json.JSONDecodeError as e:
                    print(f"❌ ID {row_id} has invalid 'itens_json': {e}")
                    print(f"   Content starts with: {itens[:50]}")
                    print(f"   Content ends with: {itens[-50:]}")
            
            # Check fotos_json
            if fotos and fotos.strip() and fotos != 'null':
                try:
                    json.loads(fotos)
                except json.JSONDecodeError as e:
                    print(f"❌ ID {row_id} has invalid 'fotos_json': {e}")
                    # print(f"   Content starts with: {fotos[:50]}")
                
        conn.close()
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    check_json()
