import os
import sys
import shutil

# Garante que podemos importar o database.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import database

def limpar_banco():
    print(f"\n[DB] Iniciando limpeza do banco ({database.ACTIVE_ENGINE})...")
    with database.get_connection() as conn:
        cur = conn.cursor()
        if database.ACTIVE_ENGINE == "postgresql":
            cur.execute("""
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
            """)
        else:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            for t in tables:
                table_name = t[0]
                if table_name != "sqlite_sequence":
                    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
    print("[DB] Tabelas removidas. Recriando estrutura base...")
    database.inicializar_banco()
    print("[DB] Estrutura e seeds padrao recriados com sucesso.")

def limpar_arquivos_sensiveis():
    root_dir = os.path.dirname(current_dir)
    print("\n[FILES] Limpando dados sensíveis e temporários...")
    
    # 1. Arquivos na pasta raiz do projeto
    arquivos = [
        "ngrok_dominio.txt",
        "ngrok_token.txt",
        "ngrok_temp.yml",
        "ngrok.log",
        os.path.join("LICENSA", "license.key"),
        os.path.join("PY", "WHATSAPP_MOTOR", "status.json"),
        os.path.join("PY", "WHATSAPP_MOTOR", "motor.log"),
        os.path.join("DATABASE", "LOG_DB.txt"),
        os.path.join("DATABASE", "motor_zap.log")
    ]
    
    # 2. Diretórios que devem ser apagados por completo
    diretorios_remover = [
        os.path.join("PY", "WHATSAPP_MOTOR", ".wwebjs_auth"),
        os.path.join("PY", "sessions"),
        os.path.join("orçamentos"), # Limpa PDFs gerados
        os.path.join("Output"),     # Limpa instaladores antigos
        os.path.join("build"),
        os.path.join("dist")
    ]

    # 3. Limpeza do LOCALAPPDATA (Crucial para o executável)
    appdata_juvicks = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'JUVICKS_DATA')
    if os.path.exists(appdata_juvicks):
        try:
            shutil.rmtree(appdata_juvicks)
            print(f"  - Limpo: Dados de Produção (LOCALAPPDATA)")
        except: pass

    # Executa remoção de arquivos
    for arq in arquivos:
        p = os.path.join(root_dir, arq)
        if os.path.exists(p):
            try:
                os.remove(p)
                print(f"  - Deletado: {arq}")
            except: pass
            
    # Executa remoção de diretórios
    for d in diretorios_remover:
        p = os.path.join(root_dir, d)
        if os.path.exists(p):
            try:
                shutil.rmtree(p)
                print(f"  - Deletado diretório: {d}")
            except: pass

    # 4. Recria pastas essenciais (vazias)
    os.makedirs(os.path.join(root_dir, "PY", "sessions"), exist_ok=True)
    os.makedirs(os.path.join(root_dir, "orçamentos"), exist_ok=True)
    print("  - Pastas essenciais recriadas vazias.")

if __name__ == "__main__":
    try:
        limpar_arquivos_sensiveis()
        limpar_banco()
        print("\n>>> Limpeza de Fabrica Concluida com Sucesso! <<<")
    except Exception as e:
        print(f"\n[ERRO] durante o reset: {e}")
