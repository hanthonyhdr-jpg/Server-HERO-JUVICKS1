import sys
import os

from PY.database import get_connection, inicializar_banco

print("Inicializando...")
inicializar_banco()

print("Conectando...")
with get_connection() as conn:
    print(type(conn))
    if 'sqlite' in str(type(conn)).lower():
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print("Tabelas SQLite:", cur.fetchall())
    elif 'psycopg2' in str(type(conn)).lower():
        cur = conn.cursor()
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        print("Tabelas PG:", cur.fetchall())
