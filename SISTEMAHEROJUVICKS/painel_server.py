# -*- coding: utf-8 -*-
"""
painel_server.py — JUVIKS HERO v2 SaaS
Servidor HTTP leve que serve o painel HTML e expõe uma API REST para:
  - Execução de comandos do .bat via opcao
  - Gestão de Tenants SaaS (criar, listar, toggle, status)
  - Diagnóstico de conexão PostgreSQL

Porta: 8089
"""

import os
import sys
import json
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# ── Garante que PY/ está no path ─────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
_PY   = os.path.join(_ROOT, "PY")
if _PY not in sys.path:
    sys.path.insert(0, _PY)

# ── Importações opcionais (carregadas com lazy para não travar o servidor) ───
def _import_saas():
    try:
        import saas_manager as sm
        return sm
    except Exception as e:
        return None

def _import_db():
    try:
        import database as db
        return db
    except Exception:
        return None

# ── CORS Headers ──────────────────────────────────────────────────────────────
_CORS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, DELETE',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

# ── Token de autenticação simples para a API SaaS ────────────────────────────
# Pode ser definido via variável de ambiente JUVIKS_API_TOKEN
_API_TOKEN = os.environ.get("JUVIKS_API_TOKEN", "juviks-saas-admin-2026")


class APIHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suprime logs de acesso repetitivos no terminal
        pass

    def _auth_ok(self) -> bool:
        """Verifica Bearer token, se estiver configurado."""
        # Se token for o padrão, aceita acesso local sem checar header
        if _API_TOKEN == "juviks-saas-admin-2026":
            return True
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {_API_TOKEN}"

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        for k, v in _CORS.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, path: str):
        try:
            with open(path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 - Arquivo HTML nao encontrado")

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except Exception:
            return {}

    # ── OPTIONS (pre-flight CORS) ────────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in _CORS.items():
            self.send_header(k, v)
        self.end_headers()

    # ── GET ──────────────────────────────────────────────────────────────────
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        # ── Painel HTML principal ────────────────────────────────────────────
        if path in ("", "/", "/index.html"):
            html_path = os.path.join(_ROOT, "TELA", "PAINEL DE CONTROLE.HTML")
            self._send_html(html_path)
            return

        # ── API: Status do servidor ──────────────────────────────────────────
        if path == "/api/status":
            db = _import_db()
            pg_ok, pg_msg = db.testar_conexao_pg() if db else (False, "database module unavailable")
            self._send_json({
                "status": "online",
                "timestamp": datetime.now().isoformat(),
                "engine": db.ACTIVE_ENGINE if db else "unknown",
                "postgresql": {"conectado": pg_ok, "mensagem": pg_msg},
                "versao": "2.0.0-saas"
            })
            return

        # ── API SaaS: Listar tenants ─────────────────────────────────────────
        if path == "/api/saas/tenants":
            sm = _import_saas()
            tenants = sm.listar_tenants() if sm else []
            self._send_json({"tenants": tenants, "total": len(tenants)})
            return

        # ── API SaaS: Listar planos ──────────────────────────────────────────
        if path == "/api/saas/planos":
            sm = _import_saas()
            planos = sm.listar_planos() if sm else []
            self._send_json({"planos": planos})
            return

        # ── API SaaS: Stats do SaaS ──────────────────────────────────────────
        if path == "/api/saas/stats":
            sm = _import_saas()
            stats = sm.stats_saas() if sm else {}
            self._send_json(stats)
            return

        # ── API SaaS: Status de um tenant ────────────────────────────────────
        if path.startswith("/api/saas/tenants/"):
            slug = path.replace("/api/saas/tenants/", "").split("/")[0]
            sm = _import_saas()
            t = sm.obter_tenant(slug) if sm else None
            if t:
                self._send_json(t)
            else:
                self._send_json({"erro": "Tenant não encontrado"}, 404)
            return

        # 404
        self._send_json({"erro": "Endpoint não encontrado"}, 404)

    # ── POST ─────────────────────────────────────────────────────────────────
    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        data = self._read_body()

        # ── Comando BAT (compatibilidade com painel original) ─────────────────
        if path == "/api/comando":
            opcao = data.get("opcao", "")
            if opcao:
                print(f"[API] Executando comando {opcao} no .bat em nova janela...")
                bat_path = os.path.join(_ROOT, "PAINEL DE CONTROLE.bat")
                cmd_str = f'start "JUVIKS RUNTIME [Opcao {opcao}]" cmd.exe /c ""{bat_path}" {opcao}"'
                subprocess.Popen(cmd_str, shell=True, cwd=_ROOT)
                self._send_json({"status": "sucesso", "opcao": opcao})
            else:
                self._send_json({"erro": "opcao não informada"}, 400)
            return

        # ── API SaaS: Criar tenant ─────────────────────────────────────────
        if path == "/api/saas/tenants":
            sm = _import_saas()
            if not sm:
                self._send_json({"erro": "SaaS manager indisponível"}, 503)
                return
            nome  = data.get("nome", "").strip()
            email = data.get("email_admin", "").strip()
            if not nome or not email:
                self._send_json({"erro": "nome e email_admin são obrigatórios"}, 400)
                return
            result = sm.criar_tenant(
                nome=nome,
                email_admin=email,
                cnpj=data.get("cnpj", ""),
                nome_fantasia=data.get("nome_fantasia", ""),
                plano_nome=data.get("plano", "Trial"),
                dias_trial=int(data.get("dias_trial", 14)),
            )
            status_code = 201 if result.get("sucesso") else 400
            self._send_json(result, status_code)
            return

        # ── API SaaS: Toggle tenant (ativar/suspender) ─────────────────────
        if path.startswith("/api/saas/tenants/") and path.endswith("/toggle"):
            slug = path.replace("/api/saas/tenants/", "").replace("/toggle", "")
            sm = _import_saas()
            if not sm:
                self._send_json({"erro": "SaaS manager indisponível"}, 503)
                return
            ativar = data.get("ativar", True)
            result = sm.toggle_tenant(slug, ativar=ativar)
            self._send_json(result)
            return

        # ── API SaaS: Verificar licença ────────────────────────────────────
        if path == "/api/saas/verificar-licenca":
            sm = _import_saas()
            chave = data.get("chave", "").strip().upper()
            if not chave:
                self._send_json({"valida": False, "erro": "Chave não informada"}, 400)
                return
            valida, slug = sm.verificar_licenca_saas(chave) if sm else (False, "")
            self._send_json({"valida": valida, "slug": slug, "chave": chave})
            return

        # ── API SaaS: Testar conexão PostgreSQL ────────────────────────────
        if path == "/api/saas/testar-pg":
            db = _import_db()
            ok, msg = db.testar_conexao_pg() if db else (False, "DB module unavailable")
            self._send_json({"conectado": ok, "mensagem": msg})
            return

        self._send_json({"erro": "Endpoint POST não encontrado"}, 404)

    # ── DELETE ────────────────────────────────────────────────────────────────
    def do_DELETE(self):
        path = self.path.split("?")[0].rstrip("/")
        if path.startswith("/api/saas/tenants/"):
            slug = path.replace("/api/saas/tenants/", "")
            sm = _import_saas()
            if not sm:
                self._send_json({"erro": "SaaS manager indisponível"}, 503)
                return
            result = sm.deletar_tenant(slug, confirmar=True)
            self._send_json(result)
            return
        self._send_json({"erro": "DELETE não encontrado"}, 404)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    PORT = int(os.environ.get("JUVIKS_PAINEL_PORT", 8089))
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, APIHandler)

    print("=" * 58)
    print("  JUVIKS HERO v2 — SERVIDOR DO PAINEL SaaS INICIADO")
    print("=" * 58)
    print(f"  Painel GUI  → http://localhost:{PORT}")
    print(f"  API Status  → http://localhost:{PORT}/api/status")
    print(f"  SaaS API    → http://localhost:{PORT}/api/saas/tenants")
    print(f"  SaaS Stats  → http://localhost:{PORT}/api/saas/stats")
    print("=" * 58)

    # Inicializa SaaS em thread separada para não travar o servidor
    def _init_bg():
        try:
            db = _import_db()
            sm = _import_saas()
            if db:
                ok, msg = db.testar_conexao_pg()
                print(f"  [PG] {msg}")
            if sm:
                stats = sm.stats_saas()
                print(f"  [SaaS] {stats.get('total_tenants', 0)} tenant(s) registrado(s)")
        except Exception as e:
            print(f"  [INIT] {e}")

    threading.Thread(target=_init_bg, daemon=True).start()
    httpd.serve_forever()
