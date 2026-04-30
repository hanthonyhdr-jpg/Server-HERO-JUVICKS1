# -*- coding: utf-8 -*-
"""
database.py — JUVIKS HERO v2 (Licença Vitalícia + PostgreSQL)
Suporta:
  - PostgreSQL standalone (schema public)
  - Fallback automático para SQLite (modo dev / modo offline)

Variáveis de controlo:
  ACTIVE_ENGINE  → 'postgresql' | 'sqlite'
"""

import os
import sys
import json
import threading
from contextlib import contextmanager
from datetime import datetime

import pandas as pd


# ──────────────────────────────────────────────────────────────────────────────
# 0. UTILITÁRIO DE LEITURA ROBUSTA — resolve UnicodeDecodeError de uma vez
# ──────────────────────────────────────────────────────────────────────────────

def ler_arquivo_seguro(path: str, modo: str = "r") -> str:
    """
    Lê um arquivo de texto de forma robusta, detectando automaticamente
    o encoding. Nunca lança UnicodeDecodeError.

    Ordem de tentativas:
      1. UTF-8 (padrão)
      2. UTF-8 com BOM (arquivos gerados pelo Notepad/Windows)
      3. Windows-1252 / Latin-1 (arquivos antigos do Windows BR)
    """
    encodings = ["utf-8", "utf-8-sig", "windows-1252", "latin-1"]
    for enc in encodings:
        try:
            with open(path, modo, encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            raise
    # Último recurso: lê com errors=replace para nunca travar
    with open(path, modo, encoding="utf-8", errors="replace") as f:
        return f.read()


def carregar_json_seguro(path: str) -> dict:
    """
    Lê e parseia um JSON de forma robusta, independente do encoding do arquivo.
    Retorna {} em caso de erro.
    """
    try:
        conteudo = ler_arquivo_seguro(path)
        return json.loads(conteudo)
    except Exception:
        return {}

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO DO ENGINE
# ──────────────────────────────────────────────────────────────────────────────

def _get_root_dir() -> str:
    """Retorna o diretório raiz do projeto (onde fica CONFIG_SISTEMA/)."""
    if getattr(sys, 'frozen', False):
        # PyInstaller OneDir modo (>= 5.0) coloca os arquivos em _internal
        # sys._MEIPASS aponta para _internal
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # __file__ está em PY/database.py → pai é SISTEMA LIMPO - ESTAVEL/
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_DIR = _get_root_dir()
CONFIG_PATH = os.path.join(ROOT_DIR, "CONFIG_SISTEMA", "db_config.json")


def _load_db_config() -> dict:
    """Carrega db_config.json; retorna configuração SQLite como fallback."""
    default = {"engine": "sqlite", "fallback_sqlite": True}
    if os.path.exists(CONFIG_PATH):
        cfg = carregar_json_seguro(CONFIG_PATH)
        if cfg:
            return cfg
    return default


_DB_CFG = _load_db_config()
ACTIVE_ENGINE: str = _DB_CFG.get("engine", "sqlite")

def _get_conn_type() -> str:
    """Retorna 'postgres' se o engine ativo for PostgreSQL, caso contrário 'sqlite'."""
    return 'postgres' if ACTIVE_ENGINE == 'postgresql' else 'sqlite'

# ──────────────────────────────────────────────────────────────────────────────
# 2. LOCALIZAÇÃO DO BANCO SQLITE (compatibilidade)
# ──────────────────────────────────────────────────────────────────────────────

def _get_data_dirs():
    try:
        # install_dir é a pasta onde o sistema foi instalado fisicamente (C:\Program Files\...)
        if getattr(sys, 'frozen', False):
            install_dir = os.path.dirname(sys.executable)
            # assets_dir é de onde pegamos arquivos imutáveis (pode ser o bundle ou a pasta do EXE)
            assets_dir = getattr(sys, '_MEIPASS', install_dir)
        else:
            install_dir = ROOT_DIR
            assets_dir = ROOT_DIR

        data_root = os.path.join(
            os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
            "JUVICKS_DATA"
        )
        
        # Se o sistema estiver em Program Files, DEVEMOS usar LOCALAPPDATA
        # No Windows, pastas em Program Files são protegidas contra escrita.
        needs_appdata = any(
            x in install_dir for x in ["Program Files", "Arquivos de Programas"]
        )

        if needs_appdata or getattr(sys, 'frozen', False):
            # Para o executável, sempre preferimos LOCALAPPDATA para garantir persistência
            os.makedirs(data_root, exist_ok=True)
            dest_db_dir = os.path.join(data_root, "DATABASE")
            os.makedirs(dest_db_dir, exist_ok=True)
            
            # Tenta localizar o banco original para migração inicial
            source_candidates = [
                os.path.join(install_dir, "DATABASE", "sistema_vendas.db"),
                os.path.join(assets_dir, "DATABASE", "sistema_vendas.db"),
                os.path.join(install_dir, "_internal", "DATABASE", "sistema_vendas.db")
            ]
            
            dest_db = os.path.join(dest_db_dir, "sistema_vendas.db")
            if not os.path.exists(dest_db):
                for src in source_candidates:
                    if os.path.exists(src):
                        import shutil
                        try:
                            shutil.copy2(src, dest_db)
                            break
                        except: pass
            return data_root, install_dir
        else:
            return install_dir, install_dir
    except Exception:
        return os.getcwd(), os.getcwd()

DATA_DIR, ASSETS_DIR = _get_data_dirs()
DB_DIR  = os.path.join(DATA_DIR, "DATABASE")
DB_PATH = os.path.normpath(os.path.join(DB_DIR, "sistema_vendas.db"))
os.makedirs(DB_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# 3. SEM TENANCY (Modo Vitalício)
# ──────────────────────────────────────────────────────────────────────────────

def set_tenant(slug: str | None):
    """Placeholder (SaaS removido)."""
    pass

def get_tenant() -> str | None:
    """Sempre retorna None (SaaS removido)."""
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 4. CONNECTION — PostgreSQL
# ──────────────────────────────────────────────────────────────────────────────
# Global state para Circuit Breaker do PostgreSQL
_PG_LAST_FAILURE_TIME = 0.0
_PG_RETRY_INTERVAL = 45  # 45s de "descanso" se o PG falhar

def _pg_dsn() -> dict:
    return {
        "host":     _DB_CFG.get("host",     "localhost"),
        "port":     _DB_CFG.get("port",     5432),
        "dbname":   _DB_CFG.get("database", "juviks_saas"),
        "user":     _DB_CFG.get("user",     "juviks_admin"),
        "password": _DB_CFG.get("password", ""),
        "connect_timeout": _DB_CFG.get("connect_timeout", 2), # Reduzido para 2s para mais agilidade
    }


@contextmanager
def _pg_connection(tenant_slug: str | None = None):
    """Abre conexão PostgreSQL no schema 'public'."""
    import psycopg2
    try:
        conn = psycopg2.connect(**_pg_dsn())
    except UnicodeDecodeError:
        raise Exception("Erro de conexão/autenticação no PostgreSQL. Verifique usuário/senha em db_config.json.")
    
    conn.set_client_encoding('UTF8')
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO public")
        conn.commit()
        yield conn
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# 5. CONNECTION — SQLite (fallback / modo dev)
# ──────────────────────────────────────────────────────────────────────────────

@contextmanager
def _sqlite_connection():
    import sqlite3
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# 6. INTERFACE PÚBLICA — get_connection / conectar
# ──────────────────────────────────────────────────────────────────────────────

def _log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

@contextmanager
def get_connection(tenant_slug: str | None = None):
    """
    Obtém conexão banco de dados de forma resiliente.
    Implementa um circuit-breaker para não travar a UI se o PG estiver fora.
    """
    global _PG_LAST_FAILURE_TIME
    import time
    
    usar_pg = (ACTIVE_ENGINE == "postgresql")
    
    # Circuit Breaker: se falhou recentemente, pula a tentativa do PG
    if usar_pg:
        if (time.time() - _PG_LAST_FAILURE_TIME) < _PG_RETRY_INTERVAL:
            usar_pg = False

    conn = None
    is_pg = False

    if usar_pg:
        try:
            import psycopg2
            try:
                conn = psycopg2.connect(**_pg_dsn())
            except UnicodeDecodeError:
                conn = None
            
            if conn:
                conn.set_client_encoding('UTF8')
                conn.autocommit = False
                with conn.cursor() as cur:
                    cur.execute("SET search_path TO public")
                conn.commit()
                is_pg = True
        except Exception as pg_err:
            _PG_LAST_FAILURE_TIME = time.time()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
                conn = None
            if not _DB_CFG.get("fallback_sqlite", True):
                raise
            _log(f"[PG FALLBACK] Servidor PG inacessível: {pg_err}")

    # Fallback SQLite se PG não conectou
    if conn is None:
        import sqlite3
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")

    try:
        yield conn
    finally:
        conn.close()


def conectar():
    """Compatibilidade com módulo de Backup (retorna conexão raw)."""
    if ACTIVE_ENGINE == "postgresql":
        try:
            import psycopg2
            try:
                conn = psycopg2.connect(**_pg_dsn())
            except UnicodeDecodeError:
                raise Exception("Erro authn PostgreSQL")
            with conn.cursor() as cur:
                cur.execute('SET search_path TO public')
            return conn
        except Exception:
            pass
    import sqlite3
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# ──────────────────────────────────────────────────────────────────────────────
# 7. SQL ADAPTATIVO (SQLite ↔ PostgreSQL)
# ──────────────────────────────────────────────────────────────────────────────

def _adapt_sql(sql: str, engine: str) -> str:
    """Converte SQL SQLite para o dialeto do engine alvo."""
    if engine != "postgresql":
        # No SQLite, apenas limpamos o COLLATE NOCASE que o sistema usa originalmente
        return sql.replace("COLLATE NOCASE", "")
    
    # Placeholders: ? → %s
    sql = sql.replace("?", "%s")
    # AUTOINCREMENT → SERIAL (em CREATE TABLE)
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    # INSERT OR IGNORE → INSERT ... ON CONFLICT DO NOTHING
    sql = sql.replace("INSERT OR IGNORE INTO", "INSERT INTO")
    # INSERT OR REPLACE → INSERT INTO (simplificado)
    sql = sql.replace("INSERT OR REPLACE INTO", "INSERT INTO")
    
    # Case Insensitivity: SQLite LIKE é case-insensitive. PG LIKE é case-sensitive.
    sql = sql.replace(" LIKE ", " ILIKE ")
    
    # COLLATE NOCASE → remove no PG
    sql = sql.replace("COLLATE NOCASE", "")
    
    # BLOB → BYTEA
    sql = sql.replace(" BLOB)", " BYTEA)")
    sql = sql.replace(" BLOB,", " BYTEA,")
    
    # Aliases: PostgreSQL não aceita aspas simples em aliases (as 'Nome').
    # Converte as 'Nome' → as "Nome"
    import re
    sql = re.sub(r"\bas\s+'([^']+)'", r'as "\1"', sql, flags=re.IGNORECASE)
    
    return sql

_orig_sql_store = {}

def _orig_sql(sql):
    return _orig_sql_store.get(id(sql), sql)


def _run_sql(conn, sql: str, params=()):
    """Executa SQL adaptando automaticamente para o engine ativo."""
    adapted = _adapt_sql(sql)
    cur = conn.cursor()
    if params:
        cur.execute(adapted, params)
    else:
        cur.execute(adapted)
    return cur


# ──────────────────────────────────────────────────────────────────────────────
# 8. INICIALIZAÇÃO DO BANCO (Schema do Tenant)
# ──────────────────────────────────────────────────────────────────────────────

_DDL_TABLES = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT, categoria TEXT, unidade TEXT, preco REAL,
    custo_processamento REAL DEFAULT 0, depreciacao REAL DEFAULT 0,
    descricao TEXT, composicao_json TEXT, img_data TEXT);

CREATE TABLE IF NOT EXISTS clientes (
    id TEXT PRIMARY KEY, nome TEXT, nome_fantasia TEXT,
    cnpj TEXT, inscricao_estadual TEXT, endereco TEXT, numero TEXT,
    cep TEXT, estado TEXT, cidade TEXT, bairro TEXT,
    telefone TEXT, email TEXT);

CREATE TABLE IF NOT EXISTS orcamentos (
    id TEXT PRIMARY KEY, cliente_id TEXT, itens_json TEXT,
    forma_pagamento TEXT, total REAL, data TEXT,
    validade_dias INTEGER, vendedor TEXT,
    status TEXT DEFAULT 'Pendente', obs_geral TEXT,
    prazo_entrega TEXT, hora_agendamento TEXT,
    fotos_json TEXT, status_producao TEXT DEFAULT 'Na Fila',
    custo_producao REAL DEFAULT 0, valor_pago REAL DEFAULT 0,
    valor_entrada REAL DEFAULT 0, taxa_cartao REAL DEFAULT 0,
    valor_liquido REAL DEFAULT 0, desconto_global REAL DEFAULT 0,
    status_pagamento TEXT DEFAULT 'Pendente',
    comprovante_base64 TEXT, data_pagamento TEXT,
    financeiro_obs TEXT, forma_pagamento_fin TEXT);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE,
    senha TEXT, nivel_acesso TEXT DEFAULT 'VENDEDOR');

CREATE TABLE IF NOT EXISTS sessoes_ativas (
    id TEXT PRIMARY KEY, usuario TEXT, senha_enc TEXT,
    chave_enc TEXT, data_criacao TIMESTAMP);

CREATE TABLE IF NOT EXISTS permissoes_usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER,
    modulo TEXT, permitido INTEGER DEFAULT 1,
    UNIQUE(usuario_id, modulo));

CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_nome TEXT, empresa_cnpj TEXT, empresa_tel TEXT,
    empresa_end TEXT, empresa_num TEXT, logo_data TEXT,
    vendedor_padrao TEXT, empresa_whatsapp TEXT,
    wpp_api_url TEXT, wpp_token TEXT, wpp_instance TEXT,
    wpp_msg_orcamento TEXT);

CREATE TABLE IF NOT EXISTS vendedores (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE);

CREATE TABLE IF NOT EXISTS formas_pagamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, taxa REAL,
    tipo TEXT, qtd_parcelas INTEGER, dias_boleto INTEGER);

CREATE TABLE IF NOT EXISTS modelos_contrato (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE,
    arquivo_bin BLOB);

CREATE TABLE IF NOT EXISTS categorias_produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE);

CREATE TABLE IF NOT EXISTS logs_acesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT,
    data_hora TEXT, ip TEXT);

CREATE TABLE IF NOT EXISTS chaves_acesso (
    id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE,
    usuario TEXT, descricao TEXT, status INTEGER DEFAULT 1,
    data_criacao TEXT, whitelist_ip TEXT,
    allowed_hours TEXT, last_ip TEXT,
    failed_attempts INTEGER DEFAULT 0);

CREATE TABLE IF NOT EXISTS projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_orcamento TEXT UNIQUE, cliente TEXT NOT NULL,
    data_orcamento DATE NOT NULL, data_aprovacao DATE,
    descricao TEXT, valor_venda REAL NOT NULL,
    status TEXT DEFAULT 'Aprovado');

CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id TEXT,
    data_gasto TEXT NOT NULL, descricao TEXT,
    categoria TEXT, valor REAL NOT NULL);

CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id TEXT,
    data_pagamento TEXT NOT NULL, valor REAL NOT NULL,
    forma_pagamento TEXT);

CREATE TABLE IF NOT EXISTS diretorios_favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, caminho TEXT UNIQUE NOT NULL,
    nome TEXT, data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
"""

_DDL_INDICES = [
    "CREATE INDEX IF NOT EXISTS idx_orc_cli ON orcamentos(cliente_id)",
    "CREATE INDEX IF NOT EXISTS idx_orc_sta ON orcamentos(status)",
    "CREATE INDEX IF NOT EXISTS idx_orc_dat ON orcamentos(data)",
    "CREATE INDEX IF NOT EXISTS idx_prod_cat ON produtos(categoria)",
    "CREATE INDEX IF NOT EXISTS idx_cli_nom ON clientes(nome)",
]

# Cache para evitar reinicialização do banco em cada rerun do Streamlit
_tenants_inicializados = {}

def inicializar_banco(tenant_slug: str | None = None):
    """
    Cria todas as tabelas do tenant (ou do banco padrão em SQLite).
    Idempotente — seguro chamar múltiplas vezes, mas processa apenas a primeira vez.
    """
    global _tenants_inicializados
    cache_key = tenant_slug or "default"
    
    # Roda migrações antes de qualquer coisa (Garante colunas em bancos legados)
    _verificar_migracoes_manuais()

    if cache_key in _tenants_inicializados:
        return

    try:
        with get_connection(tenant_slug) as conn:
            engine = "postgresql" if "psycopg2" in str(type(conn)) else "sqlite"
            cur = conn.cursor()

            # Executa DDL statement por statement
            for stmt in _DDL_TABLES.strip().split(";"):
                stmt = stmt.strip()
                if not stmt:
                    continue
                try:
                    # Adapta a DDL para o engine ativo no momento
                    adapted_stmt = _adapt_sql(stmt, engine)
                    cur.execute(adapted_stmt)
                except Exception as e:
                    _log(f"[DDL SKIP] {str(e)[:120]}")

            # Índices
            for idx in _DDL_INDICES:
                try:
                    cur.execute(idx)
                except Exception:
                    pass

            # Seeds obrigatórios
            _seed_inicial(conn, cur, engine)

            conn.commit()
            
            # Marca como inicializado apenas em caso de sucesso
            _tenants_inicializados[cache_key] = True
            
    except Exception as e:
        _log(f"[DB INIT ERROR] {e}")

def _verificar_migracoes_manuais():
    """Garante a existência de colunas novas em bancos legados."""
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            if ACTIVE_ENGINE == "postgresql":
                # No PG, o IF NOT EXISTS é nativo e seguro
                cur.execute("ALTER TABLE config ADD COLUMN IF NOT EXISTS wpp_msg_orcamento TEXT")
            else:
                # No SQLite, tentamos e ignoramos se já existir
                try: cur.execute("ALTER TABLE config ADD COLUMN wpp_msg_orcamento TEXT")
                except: pass
            conn.commit()
    except Exception as e:
        _log(f"[MIGRATION ERROR] {e}")

def _seed_inicial(conn, cur, engine):
    """Insere dados iniciais se as tabelas estiverem vazias."""
    ph = "%s" if engine == "postgresql" else "?"

    # Config da empresa
    cur.execute("SELECT COUNT(*) FROM config")
    if cur.fetchone()[0] == 0:
        cur.execute(f"INSERT INTO config (empresa_nome) VALUES ({ph})", ("JUVIKS HERO",))

    # Vendedor padrão
    try:
        if engine == "postgresql":
            cur.execute(f"INSERT INTO vendedores (nome) VALUES ({ph}) ON CONFLICT DO NOTHING", ("Admin",))
        else:
            cur.execute(f"INSERT OR IGNORE INTO vendedores (nome) VALUES ({ph})", ("Admin",))
    except Exception:
        pass

    # Categorias padrão
    cur.execute("SELECT COUNT(*) FROM categorias_produtos")
    if cur.fetchone()[0] == 0:
        cats = ["Esquadrias", "Vidros", "Estruturas", "Acessórios", "Serviços"]
        for c in cats:
            try:
                if engine == "postgresql":
                    cur.execute(f"INSERT INTO categorias_produtos (nome) VALUES ({ph}) ON CONFLICT DO NOTHING", (c,))
                else:
                    cur.execute(f"INSERT OR IGNORE INTO categorias_produtos (nome) VALUES ({ph})", (c,))
            except Exception:
                pass

    # Admin padrão
    try:
        cur.execute(f"SELECT id FROM usuarios WHERE LOWER(usuario) = LOWER({ph})", ("admin",))
        if not cur.fetchone():
            cur.execute(
                f"INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES ({ph},{ph},{ph})",
                ("admin", "admin", "ADMIN")
            )
            if engine == "postgresql":
                cur.execute(
                    f"INSERT INTO chaves_acesso (codigo, usuario, descricao, data_criacao) VALUES ({ph},{ph},{ph},{ph}) ON CONFLICT DO NOTHING",
                    ("admin", "admin", "Chave Mestra Inicial", datetime.now().strftime("%d/%m/%Y"))
                )
            else:
                cur.execute(
                    f"INSERT OR IGNORE INTO chaves_acesso (codigo, usuario, descricao, data_criacao) VALUES ({ph},{ph},{ph},{ph})",
                    ("admin", "admin", "Chave Mestra Inicial", datetime.now().strftime("%d/%m/%Y"))
                )
    except Exception as e:
        _log(f"[SEED ADMIN] {e}")


# ──────────────────────────────────────────────────────────────────────────────
# 9. FUNÇÕES PÚBLICAS DO BANCO
# ──────────────────────────────────────────────────────────────────────────────

def executar_comando(sql: str, params=()):
    """
    Executa INSERT / UPDATE / DELETE.
    Dispara exportação automática de orçamentos aprovados em thread paralela.
    """
    inicializar_banco()
    with get_connection() as conn:
        engine = "postgresql" if "psycopg2" in str(type(conn)) else "sqlite"
        adapted = _adapt_sql(sql, engine)
        
        cur = conn.cursor()
        if engine == "postgresql" and not params:
            adapted = adapted.replace("%", "%%")
            cur.execute(adapted)
        elif engine == "postgresql" and params:
            import re
            adapted = re.sub(r'%(?!s)', '%%', adapted)
            cur.execute(adapted, params)
        else:
            cur.execute(adapted, params)
        conn.commit()

        # Auto-sync financeiro em orcamentos
        sql_lower = sql.lower()
        if "orcamentos" in sql_lower and any(op in sql_lower for op in ["insert", "update", "delete"]):
            try:
                import threading as _th
                from utils.db_export import exportar_bd_aprovados
                if "status" in sql_lower and "update" in sql_lower:
                    _sync_financeiro(params, sql_lower, engine)
                _th.Thread(target=exportar_bd_aprovados, daemon=True).start()
            except Exception:
                pass


def _sync_financeiro(params, sql_lower, engine):
    """Sincroniza campos financeiros quando o status de um orçamento muda."""
    try:
        if isinstance(params, (tuple, list)) and len(params) >= 2:
            novo_status = params[0]
            orc_id = params[-1]
            ph = "%s" if engine == "postgresql" else "?"
            with get_connection() as conn:
                cur = conn.cursor()
                if novo_status == "Aprovado":
                    cur.execute(f"""
                        UPDATE orcamentos SET
                            status_pagamento = 'Pago Total',
                            valor_pago = total,
                            data_pagamento = {ph},
                            valor_liquido = total
                        WHERE id = {ph}
                    """, (datetime.now().strftime("%Y-%m-%d"), orc_id))
                elif novo_status in ["Pendente", "Cancelado"]:
                    cur.execute(f"""
                        UPDATE orcamentos SET
                            status_pagamento = 'Pendente',
                            valor_pago = 0,
                            data_pagamento = NULL
                        WHERE id = {ph}
                    """, (orc_id,))
                conn.commit()
    except Exception:
        pass


def buscar_dados(sql: str, params=()):
    """Executa SELECT e retorna DataFrame pandas."""
    inicializar_banco()
    with get_connection() as conn:
        engine = "postgresql" if "psycopg2" in str(type(conn)) else "sqlite"
        adapted = _adapt_sql(sql, engine)
        
        if engine == "postgresql":
            if not params:
                # Sem parâmetros: escapa todos os % literais para %%
                # para que psycopg2 não os interprete como placeholders
                adapted = adapted.replace("%", "%%")
                return pd.read_sql_query(adapted, conn)
            else:
                # Com parâmetros: escapa apenas % que NÃO são %s (placeholder)
                import re
                adapted = re.sub(r'%(?!s)', '%%', adapted)
                return pd.read_sql_query(adapted, conn, params=params)
        
        return pd.read_sql_query(adapted, conn, params=params)


def contar_registros(tabela: str) -> int:
    """Conta registros de uma tabela."""
    inicializar_banco()
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {tabela}")
            return cur.fetchone()[0]
    except Exception:
        return 0


# ──────────────────────────────────────────────────────────────────────────────
# 10. UTILITÁRIOS INTERNOS
# ──────────────────────────────────────────────────────────────────────────────

def _log(msg: str):
    try:
        log_dir = os.path.join(DATA_DIR, "DATABASE")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "LOG_DB.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")
    except Exception:
        pass


def testar_conexao_pg() -> tuple[bool, str]:
    """Testa a conexão com PostgreSQL. Retorna (sucesso, mensagem)."""
    if ACTIVE_ENGINE != "postgresql":
        return False, "Engine configurado como SQLite"
    try:
        import psycopg2
        try:
            conn = psycopg2.connect(**_pg_dsn())
        except UnicodeDecodeError:
            return False, "Erro de autenticação no PostgreSQL (senha ou usuário incorreto)."
        ver = conn.server_version
        conn.close()
        return True, f"PostgreSQL {ver // 10000}.{(ver // 100) % 100} conectado com sucesso!"
    except Exception as e:
        return False, str(e)


# ──────────────────────────────────────────────────────────────────────────────
# AUTO-INIT
# Removido do import global para não travar o carregamento inicial da página.
# O painel de controle ou rotinas de startup garantirão a estrutura via inicializar_banco().
# ──────────────────────────────────────────────────────────────────────────────