import sqlite3

db_path = r'h:\SISTEMAJUV\SISTEMAJUV\DATABASE\sistema_vendas.db'

def get_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='orcamentos'")
    print(cursor.fetchone()[0])
    conn.close()

if __name__ == "__main__":
    get_schema()
