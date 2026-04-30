import sys
import os

# Adiciona caminhos
current_dir = os.path.dirname(os.path.abspath(__file__))
raiz_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)

print(f"Current Dir: {current_dir}")
print(f"Raiz Dir: {raiz_dir}")

print("\n--- Testando Imports ---")
try:
    import database
    print("OK: import database")
    database.inicializar_banco()
    print("OK: database.inicializar_banco()")
except Exception as e:
    print(f"ERRO: import database: {e}")

try:
    from utils import auth_manager
    print("OK: from utils import auth_manager")
except Exception as e:
    print(f"ERRO: from utils import auth_manager: {e}")

try:
    from utils import license_manager
    print("OK: from utils import license_manager")
except Exception as e:
    print(f"ERRO: from utils import license_manager: {e}")

try:
    from utils import hardware_license
    print("OK: from utils import hardware_license")
except Exception as e:
    print(f"ERRO: from utils import hardware_license: {e}")

print("\n--- Verificando Tabelas ---")
try:
    import sqlite3
    db_path = os.path.join(raiz_dir, "DATABASE", "sistema_vendas.db")
    print(f"DB Path: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tabelas encontradas: {[t[0] for t in tables]}")
    conn.close()
except Exception as e:
    print(f"ERRO: Verificando tabelas: {e}")
