import os
import sys

# Adiciona a raiz ao path
sys.path.append(r"h:\SISTEMAJUV\SISTEMAJUV\PY")

try:
    from database import inicializar_banco, DB_PATH
    print(f"DATABASE PATH: {DB_PATH}")
    print("Iniciando inicializacao manual...")
    inicializar_banco()
    print("Sucesso!")
except Exception as e:
    import traceback
    print(f"ERRO: {e}")
    traceback.print_exc()
