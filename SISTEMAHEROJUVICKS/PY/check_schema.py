import sqlite3
conn = sqlite3.connect('h:/SISTEMAJUV/SISTEMAJUV/DATABASE/sistema_vendas.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(usuarios)")
print(cursor.fetchall())
conn.close()
