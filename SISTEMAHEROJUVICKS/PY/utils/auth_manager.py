# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys
import json
import hashlib
import uuid
import base64
from datetime import datetime
from database import buscar_dados, executar_comando, set_tenant, ACTIVE_ENGINE
from utils.hardware_license import (
    registrar_computador, 
    listar_perfis_autorizados,
    carregar_credenciais_perfil,
    apagar_perfil,
    get_full_hwid,
    enc, dec
)

# ── Pasta de sessões (Configurada para AppData para evitar erro de permissão no C:) ──
def get_safe_sessions_dir():
    try:
        if getattr(sys, 'frozen', False):
            # Se estiver instalado, usa a pasta de dados segura do Windows
            data_root = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "JUVICKS_DATA")
            path = os.path.join(data_root, "sessions")
            if not os.path.exists(path): os.makedirs(path, exist_ok=True)
            return path
        else:
            # Em desenvolvimento local
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
            if not os.path.exists(path): os.makedirs(path, exist_ok=True)
            return path
    except:
        return os.path.join(os.getcwd(), "sessions")

SESSIONS_DIR = get_safe_sessions_dir()

# ── Permissões de Módulos ──────────────────────────────────────────────────────
MODULOS_SISTEMA = [
    "Clientes", 
    "Orçamentos", 
    "Contratos", 
    "Agenda", 
    "Dashboard", 
    "Assinaturas", 
    "Financeiro", 
    "Configurações",
    "Gerenciar Liberações",
    "Painel de Controle",
    # --- SUBMENUS DETALHADOS ---
    "Financeiro - Lançamentos",
    "Financeiro - Relatórios",
    "Config - Engenharia/Produtos",
    "Config - Usuários/Permissões",
    "Config - Backup/Dados",
    "Config - Reset de Fábrica",
    "Painel - Manutenção",
    "Painel - Auditoria",
    "Liberações - Gestão de Chaves",
    "Liberações - Logs de Acesso",
    "Assinaturas - Enviar Convites",
    "Assinaturas - Dashboard/Logs",
    "Config - Motor WhatsApp"
]

def _session_file(usuario: str) -> str:
    safe = hashlib.md5(usuario.encode()).hexdigest()[:16]
    return os.path.join(SESSIONS_DIR, f"sess_{str(safe)}.json")

def excluir_sessao(usuario=None):
    """Encerra a sessão atual e remove os arquivos de persistência."""
    u = usuario or st.session_state.get("usuario_nome")
    
    # 1. Remove o arquivo de sessão persistente (Auto-login F5)
    try:
        last_sess_path = os.path.join(SESSIONS_DIR, "last_session.json")
        if os.path.exists(last_sess_path):
            os.remove(last_sess_path)
    except: pass

    # 2. Remove o arquivo de sessão específico do usuário
    if u:
        try:
            path = _session_file(u)
            if os.path.exists(path):
                os.remove(path)
        except: pass
        
    # 3. Limpa o estado do Streamlit
    st.session_state.pop("conta_bloqueada", None)
    st.session_state.pop("usuario_nome", None)
    st.session_state.pop("usuario_id", None)
    st.session_state.pop("usuario_nivel", None)
    st.session_state.autenticado = False

def esquecer_perfil_browser(usuario_nome):
    """Remove definitivamente o perfil do cache do navegador."""
    st.components.v1.html(f"""
        <script>
        (function() {{
            try {{
                const storage = window.parent.localStorage;
                let profiles = JSON.parse(storage.getItem("juv_profiles") || "{{}}");
                delete profiles["{usuario_nome}"];
                storage.setItem("juv_profiles", JSON.stringify(profiles));
                if (storage.getItem("juv_last_user") === "{usuario_nome}") {{
                    storage.removeItem("juv_last_user");
                }}
                window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + "?logout=1";
            }} catch(e) {{}}
        }})();
        </script>
    """, height=0)

# ── Tela de bloqueio ───────────────────────────────────────────────────────────
def exibir_tela_bloqueio():
    """Tela de bloqueio premium com design high-tech."""
    css = (
        "<style>"
        "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');"
        "[data-testid='stSidebar'],[data-testid='stSidebarNav'],"
        "[data-testid='collapsedControl'],header[data-testid='stHeader'],"
        "#MainMenu,footer{display:none!important;}"
        "html,body,.stApp{{background:#060a14!important;font-family:'Inter',sans-serif!important;}}"
        ".main,.block-container,[data-testid='stAppViewBlockContainer']"
        "{{max-width:660px!important;padding:8vh 1rem 2rem!important;margin:0 auto!important;}}"
        ".blk-wrap{{width:100%;background:rgba(13,20,38,.92);"
        "border:1px solid rgba(255,255,255,.07);border-radius:18px;overflow:hidden;"
        "box-shadow:0 20px 50px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.04);"
        "animation:blkIn .35s ease both;font-family:'Inter',sans-serif;}}"
        "@keyframes blkIn{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}"
        ".blk-bar{{height:3px;"
        "background:linear-gradient(90deg,#f43f5e,#a855f7,#3b82f6,#f43f5e);"
        "background-size:300%;animation:blkBar 6s linear infinite;}}"
        "@keyframes blkBar{{to{{background-position:300%}}}}"
        ".blk-body{{padding:36px 40px 32px;}}"
        ".blk-head{{display:flex;align-items:center;gap:18px;margin-bottom:24px;}}"
        ".blk-ico{{width:62px;height:62px;border-radius:14px;flex-shrink:0;"
        "background:linear-gradient(135deg,rgba(244,63,94,.14),rgba(168,85,247,.14));"
        "border:1px solid rgba(244,63,94,.22);"
        "display:flex;align-items:center;justify-content:center;"
        "font-size:28px;line-height:1;animation:icoP 3s ease-in-out infinite;}}"
        "@keyframes icoP{{"
        "0%,100%{{box-shadow:0 0 0 0 rgba(244,63,94,.2)}}"
        "50%{{box-shadow:0 0 0 9px rgba(244,63,94,0)}}}}"
        ".blk-badge{{display:inline-flex;align-items:center;gap:5px;"
        "padding:3px 10px;border-radius:100px;"
        "background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.25);"
        "color:#fb7185;font-size:.67rem;font-weight:700;"
        "letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;}}"
        ".blk-badge::before{{content:'';width:5px;height:5px;border-radius:50%;"
        "background:#f43f5e;animation:blink 1.4s ease-in-out infinite;}}"
        "@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.15}}}}"
        ".blk-title{{margin:0 0 3px;font-size:1.4rem;font-weight:800;"
        "color:#f1f5f9;letter-spacing:-.03em;}}"
        ".blk-sub{{margin:0;font-size:.83rem;color:#475569;}}"
        ".blk-sep{{height:1px;"
        "background:linear-gradient(90deg,transparent,rgba(255,255,255,.05),transparent);"
        "margin:0 0 22px;}}"
        ".blk-desc{{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);"
        "border-radius:10px;padding:16px 20px;margin-bottom:18px;"
        "color:#94a3b8;font-size:.9rem;line-height:1.7;}}"
        ".blk-desc strong{{color:#cbd5e1;font-weight:600;}}"
        ".blk-cta{{display:flex;align-items:center;gap:13px;"
        "background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.18);"
        "border-radius:10px;padding:14px 18px;}}"
        ".blk-cta-ico{{width:38px;height:38px;border-radius:9px;flex-shrink:0;"
        "background:rgba(59,130,246,.14);"
        "display:flex;align-items:center;justify-content:center;font-size:17px;}}"
        ".blk-cta-lbl{{font-size:.65rem;color:#475569;text-transform:uppercase;"
        "letter-spacing:1px;font-weight:700;margin-bottom:2px;}}"
        ".blk-cta-txt{{font-size:.88rem;color:#93c5fd;font-weight:600;}}"
        ".blk-foot{{background:rgba(0,0,0,.22);"
        "border-top:1px solid rgba(255,255,255,.04);"
        "padding:13px 40px;display:flex;align-items:center;justify-content:space-between;}}"
        ".blk-brand{{font-size:.6rem;color:#1e293b;letter-spacing:2.5px;"
        "text-transform:uppercase;font-family:'Courier New',monospace;font-weight:700;}}"
        ".blk-status{{font-size:.65rem;color:#334155;display:flex;align-items:center;gap:5px;}}"
        ".blk-status::before{{content:'';width:5px;height:5px;border-radius:50%;"
        "background:#f59e0b;animation:blink 2s ease-in-out infinite;}}"
        "div[data-testid='stButton']>button{{"
        "background:rgba(255,255,255,.04)!important;"
        "color:#475569!important;"
        "border:1px solid rgba(255,255,255,.07)!important;"
        "border-radius:9px!important;"
        "font-family:'Inter',sans-serif!important;"
        "font-size:.83rem!important;font-weight:500!important;"
        "padding:9px!important;transition:all .2s ease!important;"
        "margin-top:12px!important;width:100%!important;}}"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)

    st.markdown("""
    <div class="blk-wrap">
      <div class="blk-bar"></div>
      <div class="blk-body">
        <div class="blk-head">
          <div class="blk-ico">&#128274;</div>
          <div>
            <div class="blk-badge">Acesso Suspenso</div>
            <h2 class="blk-title">Conta Bloqueada</h2>
            <p class="blk-sub">Verifica&ccedil;&atilde;o necess&aacute;ria para continuar</p>
          </div>
        </div>
        <div class="blk-sep"></div>
        <div class="blk-desc">
          Seu acesso est&aacute; temporariamente <strong>suspenso</strong>.
          Isso ocorre quando sua chave &eacute; bloqueada pelo administrador
          ou quando suas credenciais precisam de atualiza&ccedil;&atilde;o.
        </div>
        <div class="blk-cta">
          <div class="blk-cta-ico">&#128222;</div>
          <div>
            <div class="blk-cta-lbl">A&ccedil;&atilde;o Recomendada</div>
            <div class="blk-cta-txt">Entre em contato com o administrador</div>
          </div>
        </div>
      </div>
      <div class="blk-foot">
        <span class="blk-brand">HERO JUVIKS SYSTEM</span>
        <span class="blk-status">Aguardando libera&ccedil;&atilde;o</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("\u2190 Voltar ao Login", use_container_width=True):
            st.session_state.pop("conta_bloqueada", None)
            excluir_sessao()
            st.rerun()

def salvar_acesso_log(usuario):
    try:
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        executar_comando("INSERT INTO logs_acesso (usuario, data_hora, ip) VALUES (?, ?, ?)", (usuario, data_hora, "Autenticado"))
    except: pass

@st.cache_data(ttl=600) # Cache de 10 minutos para dados da empresa
def obter_dados_empresa():
    """Retorna o nome da empresa e o logo em base64, com cache para performance."""
    try:
        df_conf = buscar_dados("SELECT empresa_nome, logo_data FROM config LIMIT 1")
        nome = "HERO JUVIKS SERVER"
        logo = ""
        if not df_conf.empty:
            if df_conf.iloc[0]['empresa_nome']: 
                nome = df_conf.iloc[0]['empresa_nome']
            if df_conf.iloc[0]['logo_data']: 
                logo = f"data:image/png;base64,{df_conf.iloc[0]['logo_data']}"
        return nome, logo
    except:
        return "HERO JUVIKS SERVER", ""

def resolver_tenant():
    """SaaS Removido: O sistema agora opera em schema único (public)."""
    set_tenant(None)
    return None

def _tentar_restaurar_sessao():
    """Lê o arquivo de sessão do disco e restaura a autenticação automaticamente (após F5/reload)."""
    try:
        sess_file = os.path.join(SESSIONS_DIR, "last_session.json")
        if not os.path.exists(sess_file):
            return
        with open(sess_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        user  = data.get("user", "")
        p_enc = data.get("p_enc", "")
        k_enc = data.get("k_enc", "")
        nivel = data.get("nivel", "ADMIN")
        uid   = data.get("uid", 0)
        ts    = data.get("ts", "")
        
        if not user or not p_enc:
            return
        
        # Verifica validade (30 dias)
        if ts:
            saved = datetime.fromisoformat(ts)
            if (datetime.now() - saved).days > 30:
                os.remove(sess_file)
                return
        
        password = base64.b64decode(p_enc).decode()
        key      = base64.b64decode(k_enc).decode() if k_enc else ""
        
        # Valida as credenciais no banco antes de restaurar
        res_user = buscar_dados(
            "SELECT * FROM usuarios WHERE LOWER(usuario) = ? AND senha = ?",
            (user.lower(), password)
        )
        if res_user.empty:
            return
        
        # Verifica se a chave ainda é válida e ativa
        res_key = buscar_dados(
            "SELECT * FROM chaves_acesso WHERE UPPER(codigo) = ? AND LOWER(usuario) = ? AND status = 1",
            (key.upper(), user.lower())
        )
        if res_key.empty:
            # Chave inválida ou bloqueada — remove sessão e força novo login
            try: os.remove(sess_file)
            except: pass
            return
        
        # Restaura a sessão
        st.session_state.autenticado   = True
        st.session_state.usuario_nome  = user
        st.session_state.chave_usada   = key
        st.session_state.temp_pass     = password
        st.session_state.usuario_nivel = nivel
        st.session_state.usuario_id    = uid
        st.session_state.manter_acesso = True
    except Exception:
        pass  # Sessão inválida, ignora silenciosamente

def verificar_autenticacao():
    from utils.license_manager import verificar_licenca
    
    # --- BYPASS PARA ORÇAMENTO DIGITAL (CLIENTE) ---
    # Se estivermos na página de visualização de orçamento, permitimos o acesso público
    try:
        # Detecta se é a página do orçamento pelo script_path ou parmetro
        params = st.query_params
        if "id" in params and any(x in st.session_state.get("current_page", "") for x in ["Orcamento", "Visualizar"]):
            return # Permite acesso sem login
    except: pass

    # --- SEM TENANCY (Licença Vitalícia) ---
    resolver_tenant()
    
    verificar_licenca()
    if st.session_state.get("conta_bloqueada"):
        exibir_tela_bloqueio(); st.stop()
    if not st.session_state.get("autenticado"):
        # Tenta restaurar sessão do arquivo (funciona após F5/reload)
        _tentar_restaurar_sessao()
    if not st.session_state.get("autenticado"):
        exibir_tela_login(); st.stop()

    # --- INJEÇÃO DE CSS PARA OCULTAR MENUS DA BARRA LATERAL ---
    # Só faz se estiver autenticado e não for Admin
    if st.session_state.get("usuario_nivel") != "ADMIN":
        from utils.auth_manager import obter_permissoes_usuario
        uid = st.session_state.get("usuario_id")
        if uid:
            perms = obter_permissoes_usuario(uid)
            css_hide = ""
            
            # Mapeia Módulos para o texto do link na Sidebar
            # (Streamlit usa o nome do arquivo, ex: "1 1 Clientes", "97 Configuracao Zap")
            mapa_sidebar = {
                "Clientes": "Clientes",
                "Orçamentos": "Orçamentos",
                "Contratos": "Contratos",
                "Agenda": "AGENDA",
                "Dashboard": "DASHBOARD",
                "Assinaturas": "Assinaturas",
                "Financeiro": "Financeiro",
                "Configurações": "Configuracoes_do_Sistema",
                "Gerenciar Liberações": "Gerenciar_Liberacoes",
                "Painel de Controle": "Painel_Controle",
                "Config - Motor WhatsApp": "Configuracao_Zap"
            }
            
            for modulo, palavra_chave in mapa_sidebar.items():
                if not perms.get(modulo, True):
                    css_hide += f'''
                        [data-testid="stSidebarNav"] a[href*="{palavra_chave}"],
                        [data-testid="stSidebarNav"] li:has(a[href*="{palavra_chave}"]) {{
                            display: none !important;
                        }}
                    '''
            if css_hide:
                st.markdown(f"<style>{css_hide}</style>", unsafe_allow_html=True)

def _autenticar(user: str, password: str, key: str):
    # Normaliza tudo para minúsculo — compatível com PostgreSQL e SQLite
    user = user.strip().lower()
    password = password.strip()
    key  = key.strip().upper()   # chaves são sempre salvas em maiúsculo

    # Busca usuário (comparação case-insensitive via LOWER no SQL)
    res_user = buscar_dados(
        "SELECT * FROM usuarios WHERE LOWER(usuario) = ? AND senha = ?",
        (user, password)
    )
    # Busca chave vinculada ao usuário
    res_key = buscar_dados(
        "SELECT * FROM chaves_acesso WHERE UPPER(codigo) = ? AND LOWER(usuario) = ?",
        (key, user)
    )

    if not res_user.empty and not res_key.empty:
        if res_key.iloc[0]['status'] == 1:
            # Salva sessão completa (com credenciais codificadas) para auto-restore no F5
            p_enc = base64.b64encode(password.encode()).decode()
            k_enc = base64.b64encode(key.encode()).decode()
            session_data = {
                "user": user,
                "p_enc": p_enc,
                "k_enc": k_enc,
                "nivel": res_user.iloc[0].get('nivel_acesso', 'ADMIN'),
                "uid": int(res_user.iloc[0]['id']),
                "ts": datetime.now().isoformat()
            }
            try:
                with open(os.path.join(SESSIONS_DIR, "last_session.json"), "w", encoding="utf-8") as f:
                    json.dump(session_data, f)
            except: pass
            st.session_state.autenticado    = True
            st.session_state.usuario_nome   = user
            st.session_state.chave_usada    = key
            st.session_state.temp_pass      = password
            st.session_state.usuario_nivel  = session_data["nivel"]
            st.session_state.usuario_id     = session_data["uid"]
            return True
        else:
            st.session_state.conta_bloqueada = True
            st.rerun()
    return False


def registrar_acesso_salvo():
    """Garante que a conta seja salva ou atualizada no LOCAL correto."""
    if not st.session_state.get("autenticado"):
        return

    u = st.session_state.get("usuario_nome")
    p = st.session_state.get("temp_pass")
    k = st.session_state.get("chave_usada")
    manter = st.session_state.get("manter_acesso", True)
    
    if not u or not p or not k or not manter: return

    # Identifica se é local para salvar no Hardware
    try:
        # Acesso ultra-seguro para evitar quedas em versões antigas
        ctx = getattr(st, "context", None)
        hdr = getattr(ctx, "headers", {}) if ctx else {}
        host = hdr.get("Host", "").lower() if hasattr(hdr, "get") else ""
        
        is_local = any(x in host for x in ["localhost", "127.0.0.1", "192.168.", "10.", "172."])
        if is_local:
            registrar_computador(u, p, k)
    except: pass

    # --- ESCUDO DE SESSÃO (DB + COOKIE) ---
    sid = str(uuid.uuid4())[:20]
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        p_enc = base64.b64encode(p.encode()).decode()
        k_enc = base64.b64encode(k.encode()).decode()
        executar_comando(
            "INSERT OR REPLACE INTO sessoes_ativas (id, usuario, senha_enc, chave_enc, data_criacao) VALUES (?, ?, ?, ?, ?)", 
            (sid, u, p_enc, k_enc, dt)
        )
        
        # Injetamos o cookie de forma segura
        # Usamos uma string limpa para evitar quebras de aspas no HTML
        t_slug = st.session_state.get("tenant_slug", "")
        js_cmd = (
            f"const c = 'juv_sid={sid}; path=/; max-age=2592000; SameSite=Lax'; "
            f"document.cookie = c; "
            f"try {{ if(window.parent) window.parent.document.cookie = c; }} catch(e) {{}} "
            f"const s = window.localStorage; if(s) {{ "
            f"let pr = JSON.parse(s.getItem('juv_profiles') || '{{}}'); "
            f"pr['{u}'] = {{ u: '{u}', s: '{p_enc}', k: '{k_enc}', ts: new Date().getTime() }}; "
            f"s.setItem('juv_profiles', JSON.stringify(pr)); s.setItem('juv_last_user', '{u}'); }} "
            f"console.log('JUVIKS: Sincronizado.');"
        )
        st.markdown(f'<img src="x" onerror="{js_cmd}" style="display:none;">', unsafe_allow_html=True)
    except: pass

def exibir_tela_login():
    # ── 1. VERIFICA QUERY PARAMS PRIMEIRO (antes de qualquer render) ──
    params = st.query_params
    if "login_u" in params and "login_p" in params:
        u_in  = params.get("login_u", "")
        p_in  = params.get("login_p", "")
        k_in  = params.get("login_k", "")
        
        chave_val = k_in.strip() if k_in.strip() else ("admin" if u_in.strip().lower() == "admin" else "")
        if _autenticar(u_in.strip(), p_in, chave_val):
            st.session_state.manter_acesso = True
            st.session_state.temp_pass = p_in
            salvar_acesso_log(u_in.strip())
            st.query_params.clear()
            st.rerun()
            return
        else:
            # Se falhou, limpa para evitar loop e recarrega a tela de login limpa
            st.query_params.clear()
            st.rerun()

    # ── 2. CSS: esconde sidebar e mostra iframe fullscreen ──
    st.markdown("""
        <style>
        #MainMenu, header, footer, [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stSidebar"],
        section[data-testid="stSidebar"], .stSidebar {
            display: none !important;
        }
        .stApp { background: #020b18 !important; overflow: hidden !important; }
        .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
        iframe { border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # ── 3. RENDER DO HERO HTML COMPLETO ──
    try:
        from TEMAS.login_html import LOGIN_HTML
        import streamlit.components.v1 as components
        components.html(LOGIN_HTML, height=900, scrolling=False)
    except Exception as e:
        # Fallback: formulário nativo estilizado
        st.error(f"Erro ao carregar tela de login: {e}")
        with st.form("login_fallback"):
            u_in = st.text_input("Usuário")
            p_in = st.text_input("Senha", type="password")
            k_in = st.text_input("Chave")
            if st.form_submit_button("Entrar"):
                chave_val = k_in.strip() if k_in.strip() else ("admin" if u_in.strip().lower() == "admin" else "")
                if _autenticar(u_in.strip(), p_in, chave_val):
                    st.session_state.manter_acesso = True
                    st.session_state.temp_pass = p_in
                    salvar_acesso_log(u_in.strip())
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas.")




def verificar_nivel_acesso(niveis):
    nivel = st.session_state.get("usuario_nivel", "ADMIN")
    if st.session_state.get("usuario_nome") == "admin": return True
    if nivel not in niveis:
        st.warning("⛔ Acesso restrito."); st.stop()
def obter_permissoes_usuario(usuario_id):
    """Retorna um dicionário com as permissões do usuário."""
    df = buscar_dados("SELECT modulo, permitido FROM permissoes_usuario WHERE usuario_id = ?", (usuario_id,))
    permissoes = {mod: True for mod in MODULOS_SISTEMA} # Default True para compatibilidade
    if not df.empty:
        for _, r in df.iterrows():
            permissoes[r['modulo']] = bool(r['permitido'])
    return permissoes

def salvar_permissoes_usuario(usuario_id, permissoes_dict):
    """Salva as permissões granulares do usuário usando UPSERT (PostgreSQL e SQLite)."""
    from database import executar_comando, ACTIVE_ENGINE

    for modulo, permitido in permissoes_dict.items():
        valor = 1 if permitido else 0
        if ACTIVE_ENGINE == 'postgresql':
            # PostgreSQL: UPSERT atômico — nunca lança UniqueViolation
            executar_comando(
                """INSERT INTO permissoes_usuario (usuario_id, modulo, permitido)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (usuario_id, modulo) DO UPDATE SET permitido = EXCLUDED.permitido""",
                (usuario_id, modulo, valor)
            )
        else:
            # SQLite: INSERT OR REPLACE
            executar_comando(
                "INSERT OR REPLACE INTO permissoes_usuario (usuario_id, modulo, permitido) VALUES (?, ?, ?)",
                (usuario_id, modulo, valor)
            )



def verificar_permissao_modulo(modulo_nome):
    """
    Verifica se o usuário logado tem acesso ao módulo solicitado.
    Geralmente chamado no topo de cada página.
    """
    if "usuario_id" not in st.session_state:
        return False
    
    # Administrador Master sempre tem acesso a tudo
    if st.session_state.get("usuario_nivel") == "ADMIN":
        return True
        
    usuario_id = st.session_state.get("usuario_id")
    df = buscar_dados("SELECT permitido FROM permissoes_usuario WHERE usuario_id = ? AND modulo = ?", 
                      (usuario_id, modulo_nome))
    
    if df.empty:
        return True # Se não houver regra, permite por padrão (ou mude para False se quiser segurança máxima)
        
    permitido = bool(df.iloc[0]['permitido'])
    if not permitido:
        st.error(f"🚫 Acesso Negado: Você não tem permissão para acessar o item '{modulo_nome}'.")
        st.stop()
        return False
    return True

def tem_permissao(modulo_nome):
    """Retorna True/False sem travar a execução (para uso em IFs de UI)."""
    if st.session_state.get("usuario_nivel") == "ADMIN" or st.session_state.get("usuario_nome") == "admin":
        return True
    usuario_id = st.session_state.get("usuario_id")
    if not usuario_id: return False
    df = buscar_dados("SELECT permitido FROM permissoes_usuario WHERE usuario_id = ? AND modulo = ?", 
                      (usuario_id, modulo_nome))
    if df.empty: return True
    return bool(df.iloc[0]['permitido'])
