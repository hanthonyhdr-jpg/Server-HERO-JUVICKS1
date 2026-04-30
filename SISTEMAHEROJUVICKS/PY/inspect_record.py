import sqlite3
import os

db_path = r'h:\renova\sistema_vendas.db'

def inspect_record(id_val):
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, itens_json, fotos_json FROM orcamentos WHERE id = ?", (id_val,))
        row = cursor.fetchone()
        
        if row:
            print(f"--- ID: {row[0]} ---")
            print(f"itens_json (first 300 chars): {row[1][:300]}")
            print(f"itens_json (last 300 chars): {row[1][-300:]}")
            print(f"Length: {len(row[1])}")
        else:
            print("Record not found.")
                
        conn.close()
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    inspect_record('ORC-2602260848')
