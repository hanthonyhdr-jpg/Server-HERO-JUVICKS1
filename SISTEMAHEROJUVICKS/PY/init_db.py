# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import inicializar_banco, buscar_dados

print("Inicializando banco SQLite...")

try:
    inicializar_banco()
    print("Banco inicializado!")
    
    df = buscar_dados("SELECT usuario, senha, nivel_acesso FROM usuarios")
    print("\nUsuários criados:")
    print(df)
    
    df_chaves = buscar_dados("SELECT codigo, usuario, descricao FROM chaves_acesso")
    print("\nChaves criadas:")
    print(df_chaves)
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()