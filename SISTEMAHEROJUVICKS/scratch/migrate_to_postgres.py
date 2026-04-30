import sqlite3
import psycopg2
import json
import os
import sys

# 1. Carregar configuração do PostgreSQL
CONFIG_PATH = 'CONFIG_SISTEMA/db_config.json'
if not os.path.exists(CONFIG_PATH):
    print(f"Erro: {CONFIG_PATH} não encontrado.")
    sys.exit(1)

with open(CONFIG_PATH, 'r') as f:
    db_config = json.load(f)

# 2. Conectar aos bancos
sqlite_path = 'ssdata/sistema_vendas.db'
if not os.path.exists(sqlite_path):
    print(f"Erro: {sqlite_path} não encontrado.")
    sys.exit(1)

try:
    lite_conn = sqlite3.connect(sqlite_path)
    lite_curr = lite_conn.cursor()
    print("[OK] Conectado ao SQLite antigo.")
    
    pg_conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['user'],
        password=db_config['password']
    )
    pg_curr = pg_conn.cursor()
    print("[OK] Conectado ao PostgreSQL.")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    sys.exit(1)

# 3. Mapeamento de Tabelas e Lógica de Migração
def migrate_table(table_name):
    print(f"Migrando tabela: {table_name}...")
    try:
        # Ler colunas do SQLite
        lite_curr.execute(f"PRAGMA table_info({table_name})")
        cols_info = lite_curr.fetchall()
        cols = [row[1] for row in cols_info]
        col_names = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))
        
        # Se for a tabela de imagens, garantir que ela exista no PG
        if table_name == 'producao_imagens':
            pg_curr.execute("""
                CREATE TABLE IF NOT EXISTS producao_imagens (
                    id SERIAL PRIMARY KEY,
                    orcamento_id TEXT,
                    imagem_blob BYTEA,
                    data_upload TEXT
                )
            """)
            pg_conn.commit()

        # Ler dados do SQLite
        lite_curr.execute(f"SELECT {col_names} FROM {table_name}")
        rows = lite_curr.fetchall()
        
        if not rows:
            print(f"  - Tabela {table_name} está vazia. Pulando.")
            return

        # Ajuste de tipos para PostgreSQL (ex: converte blobs ou strings binárias)
        cleaned_rows = []
        for row in rows:
            new_row = []
            for i, val in enumerate(row):
                col_name = cols[i]
                
                # Correção específica para permissoes_usuario (usuario_id)
                if table_name == 'permissoes_usuario' and col_name == 'usuario_id':
                    try:
                        if isinstance(val, bytes):
                            new_row.append(int(val.decode('utf-8', errors='ignore')))
                        else:
                            new_row.append(int(val))
                    except:
                        new_row.append(None) # Fallback
                elif isinstance(val, bytes):
                    new_row.append(psycopg2.Binary(val))
                else:
                    new_row.append(val)
            cleaned_rows.append(tuple(new_row))

        # Inserir no PostgreSQL
        insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        pg_curr.executemany(insert_query, cleaned_rows)
        pg_conn.commit()
        print(f"  - [SUCESSO] {len(rows)} registros migrados para {table_name}.")
        
    except Exception as e:
        print(f"  - [ERRO] Falha ao migrar {table_name}: {e}")
        pg_conn.rollback()

# Lista de tabelas para migrar (na ordem correta para evitar erros de FK se houver)
tables_to_migrate = [
    'config', 'categorias_produtos', 'vendedores', 'usuarios', 
    'clientes', 'produtos', 'orcamentos', 'formas_pagamento', 
    'modelos_contrato', 'producao_imagens', 'logs_acesso', 
    'chaves_acesso', 'gastos', 'entradas', 'projetos', 
    'diretorios_favoritos', 'permissoes_usuario'
]

for table in tables_to_migrate:
    # Verifica se a tabela existe no SQLite antes de tentar
    lite_curr.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
    if lite_curr.fetchone():
        migrate_table(table)
    else:
        print(f"Tabela {table} não existe no SQLite. Pulando.")

# 4. Finalização
lite_conn.close()
pg_conn.close()
print("\n>>> MIGRAÇÃO CONCLUÍDA!")
