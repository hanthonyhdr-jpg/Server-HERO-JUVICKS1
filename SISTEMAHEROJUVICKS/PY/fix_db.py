import sqlite3

db_path = r'h:\SISTEMAJUV\SISTEMAJUV\DATABASE\sistema_vendas.db'

def fix_record(id_val):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # We replace the corrupted JSON with a valid empty list
        print(f"Fixing record {id_val}...")
        cursor.execute("UPDATE orcamentos SET itens_json = '[]' WHERE id = ?", (id_val,))
        conn.commit()
        print("Success!")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_record('ORC-2602260848')
