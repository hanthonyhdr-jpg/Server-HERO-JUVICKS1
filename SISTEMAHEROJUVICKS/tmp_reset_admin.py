import sqlite3
from datetime import datetime

try:
    conn = sqlite3.connect('DATABASE/sistema_vendas.db')
    cursor = conn.cursor()
    
    # 1. Limpeza TOTAL do admin
    cursor.execute("DELETE FROM usuarios WHERE usuario = 'admin' COLLATE NOCASE")
    cursor.execute("DELETE FROM chaves_acesso WHERE usuario = 'admin' COLLATE NOCASE")
    
    # 2. Insercao Segura de novo Admin
    cursor.execute("INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES (?, ?, ?)", 
                   ('admin', 'juvix', 'ADMIN'))
    cursor.execute("INSERT INTO chaves_acesso (codigo, usuario, status, data_criacao) VALUES (?, ?, ?, ?)", 
                   ('admin', 'admin', 1, datetime.now().strftime("%d/%m/%Y")))
    
    conn.commit()
    conn.close()
    print("[OK] CREDENCIAIS MASTER RESETADAS!")
    print("USUARIO: admin | SENHA: juvix | CHAVE: admin")
except Exception as e:
    print(f"[ERRO] Falha ao resetar banco: {e}")
