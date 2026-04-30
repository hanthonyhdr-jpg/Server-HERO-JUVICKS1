import streamlit as st
import os, sys, sqlite3, uuid, base64, io, time, hashlib, requests
from datetime import datetime
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

# ─── PATHS ────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    ROOT_DIR = os.path.join(sys._MEIPASS, "PY")
    # Pasta onde está o executável (.exe)
    EXE_DIR = os.path.dirname(sys.executable)
    
    # Se estivermos rodando de dentro da pasta 'dist' (durante testes), 
    # tentamos usar a raiz do projeto (um nível acima) para achar o DATABASE.
    if not os.path.exists(os.path.join(EXE_DIR, "DATABASE")) and os.path.basename(EXE_DIR).lower() == 'dist':
        SYS_ROOT = os.path.dirname(EXE_DIR)
    else:
        SYS_ROOT = EXE_DIR
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SYS_ROOT = os.path.dirname(ROOT_DIR)

# IMPORTANTE: DATA_ROOT deve ser persistente (LOCALAPPDATA) quando compilado
if getattr(sys, 'frozen', False):
    base_persistente = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "JUVICKS_DATA")
    DATA_ROOT = os.path.join(base_persistente, "PY")
    SYS_DB_PATH = os.path.join(base_persistente, "DATABASE", "sistema_vendas.db")
else:
    DATA_ROOT = ROOT_DIR 
    SYS_DB_PATH = os.path.join(os.path.dirname(ROOT_DIR), "DATABASE", "sistema_vendas.db")

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Diretorios de dados (Devem ser persistentes)
ASSI_DIR    = os.path.join(DATA_ROOT, "assiname_app")
ASSI_DB     = os.path.join(ASSI_DIR, "assinaturas.db")
UPLOADS_DIR = os.path.join(ASSI_DIR, "uploads")
SIGNED_DIR  = os.path.join(ASSI_DIR, "signed")

# Garante que as pastas de dados existam fora do _MEIPASS
for d in [ASSI_DIR, UPLOADS_DIR, SIGNED_DIR]:
    os.makedirs(d, exist_ok=True)

# Caminho para os utilitarios de codigo (Estao no _MEIPASS)
CODE_ASSI_DIR = os.path.join(ROOT_DIR, "assiname_app")

# ─── IMPORTS do módulo ASSINAME (Robust) ──────────────────────────────────────
try:
    # 1. Tenta import direto
    import assiname_app.sig_utils as assi_utils
    sign_pdf = assi_utils.sign_pdf
except ImportError:
    # 2. Fallback absoluto se o import falhar (necessário em alguns casos do PyInstaller)
    import importlib.util
    _path = os.path.join(CODE_ASSI_DIR, "sig_utils.py")
    
    # Failsafe para PyInstaller: verifica se o arquivo existe
    if not os.path.exists(_path):
        # Se estiver no _internal mas não achar com 'PY', tenta sem o prefixo 'PY'
        if "\\PY\\" in _path: _alt = _path.replace("\\PY\\", "\\")
        elif "/PY/" in _path: _alt = _path.replace("/PY/", "/")
        else: _alt = _path # Fallback
        
        if os.path.exists(_alt): _path = _alt

    spec = importlib.util.spec_from_file_location("assiname_utils", _path)
    assi_utils = importlib.util.module_from_spec(spec)
    sys.modules["assiname_utils"] = assi_utils
    spec.loader.exec_module(assi_utils)
    sign_pdf = assi_utils.sign_pdf

# ─── DB HELPERS ───────────────────────────────────────────────────────────────
def db_conn():
    conn = sqlite3.connect(ASSI_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_assi_db():
    conn = db_conn()
    conn.execute('''CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY, original_filename TEXT NOT NULL,
        filename TEXT NOT NULL, whatsapp_number TEXT NOT NULL,
        status TEXT DEFAULT 'pending', created_at TEXT,
        client_ip TEXT, client_location TEXT, client_device_id TEXT,
        client_signature_time TEXT, sender_ip TEXT, sender_signature_time TEXT,
        client_name TEXT
    )''')
    try: conn.execute("ALTER TABLE documents ADD COLUMN client_name TEXT")
    except: pass
    try: conn.execute("ALTER TABLE documents ADD COLUMN razao_social TEXT")
    except: pass
    try: conn.execute("ALTER TABLE documents ADD COLUMN numero_pedido TEXT")
    except: pass
    conn.commit(); conn.close()

init_assi_db()

def get_docs(status_filter=None):
    conn = db_conn()
    if status_filter:
        rows = conn.execute(
            "SELECT * FROM documents WHERE status=? ORDER BY created_at DESC",
            (status_filter,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows

def get_doc(doc_id):
    conn = db_conn()
    doc = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    return doc

def count_docs(status=None):
    conn = db_conn()
    if status:
        r = conn.execute("SELECT COUNT(*) FROM documents WHERE status=?", (status,)).fetchone()[0]
    else:
        r = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()
    return r

def enviar_whatsapp_api(numero, mensagem):
    """Envia mensagem automática via Motor Próprio (localhost:3000)."""
    try:
        # Endereço do nosso Motor Próprio Integrado
        url = "http://127.0.0.1:3000/send-message"
        headers = {"Content-Type": "application/json"}
        
        # Limpa o número (remove caracteres não numéricos)
        numero_limpo = "".join(filter(str.isdigit, str(numero)))
        if len(numero_limpo) <= 11:
            numero_limpo = "55" + numero_limpo
            
        payload = {
            "number": numero_limpo,
            "message": mensagem
        }
        
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if res.status_code == 200:
            return True, "Enviado via Motor Próprio!"
        return False, f"Erro no Motor: {res.text}"
    except Exception as e:
        return False, f"Motor Offline: {str(e)}"

def get_ngrok_url():
    try:
        r = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if r.status_code == 200:
            for t in r.json().get("tunnels", []):
                if t.get("public_url"):
                    return t["public_url"]
    except:
        pass
    return None

def link_cliente(doc_id):
    """Gera o link de assinatura para o cliente (via Ngrok ou localhost)."""
    base = get_ngrok_url() or "http://localhost:8501"
    return f"{base}/8-Assinaturas?sign={doc_id}"

def canvas_to_base64(canvas_result):
    """Converte resultado do st_canvas em base64 PNG."""
    if canvas_result.image_data is None:
        return None
    img_arr = canvas_result.image_data.astype("uint8")
    if img_arr.sum() == 0:
        return None
    img = Image.fromarray(img_arr, "RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def text_to_signature_base64(text, font_name="segoesc.ttf", font_size=40):
    """Converte texto em uma imagem base64 de assinatura usando uma fonte artística."""
    if not text:
        return None
    
    # Criar uma imagem transparente
    width, height = 500, 100
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Tenta carregar a fonte, se falhar usa a padrão
    try:
        # Procurar no Windows Fonts se for o caso
        font_paths = [
            font_name, 
            os.path.join("C:\\Windows\\Fonts", font_name),
            "arial.ttf"
        ]
        font = None
        for path in font_paths:
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except: continue
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Calcular posição centralizada (versões recentes do PIL usam textbbox)
    try:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        w, h = right - left, bottom - top
    except:
        w, h = draw.textsize(text, font=font) # fallback legado
        
    x = (width - w) / 2
    y = (height - h) / 2
    
    # Desenhar o texto (Azul Escuro pra parecer caneta)
    draw.text((x, y), text, fill=(30, 64, 175), font=font)
    
    # Salvar em Bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def text_to_signature_base64(text, font_name="segoesc.ttf", font_size=40):
    """Converte texto em uma imagem base64 de assinatura usando uma fonte artística."""
    if not text: return None
    width, height = 500, 100
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    try:
        font_paths = [font_name, os.path.join("C:\\Windows\\Fonts", font_name), "arial.ttf"]
        font = next((ImageFont.truetype(p, font_size) for p in font_paths if os.path.exists(p) or "\\" not in p), ImageFont.load_default())
    except: font = ImageFont.load_default()
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        w, h = r - l, b - t
    except: w, h = draw.textsize(text, font=font)
    draw.text(((width - w) / 2, (height - h) / 2), text, fill=(30, 64, 175), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def file_to_base64(uploaded):
    """Converte arquivo uploaded em base64 com header."""
    if not uploaded:
        return None
    ext = uploaded.name.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    b64 = base64.b64encode(uploaded.read()).decode()
    return f"data:{mime};base64,{b64}"

# ─── CSS GLOBAL agora é gerenciado pelo TEMAS/moderno.py ──────────────────────────
# CSS removido daqui para evitar conflitos de estilo
CSS = ""

# ══════════════════════════════════════════════════════════════════════════════
#  ROTEAMENTO: verifica se é página pública do cliente
# ══════════════════════════════════════════════════════════════════════════════
params = st.query_params
sign_id = params.get("sign", None)

if sign_id:
    # ─────────────────────── PÁGINA PÚBLICA DO CLIENTE ───────────────────────
    st.set_page_config(
        page_title="Assinar Documento | JUVIKS07",
        layout="centered", page_icon="✍️"
    )
    
    # Esconde sidebar, navegação e rodapé — cliente não pode ver o sistema
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarNav"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        .stDeployButton { display: none !important; }
        div[data-testid="stToolbar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    from TEMAS.moderno import get_signature_client_style
    st.markdown(get_signature_client_style(), unsafe_allow_html=True)

    doc = get_doc(sign_id)

    if not doc:
        st.error("❌ Documento não encontrado ou link inválido.")
        st.stop()

    # Busca razão social da empresa no banco de dados do sistema
    # Busca razão social da empresa no banco de dados do sistema via helper centralizado
    try:
        from database import buscar_dados as _bd
        _df_row = _bd("SELECT empresa_nome, logo_data FROM config LIMIT 1")
        if not _df_row.empty:
            _row = _df_row.iloc[0]
            empresa_nome = _row["empresa_nome"] if _row["empresa_nome"] else "JUVIKS"
            logo_b64     = _row["logo_data"] if _row["logo_data"] else None
        else:
            empresa_nome = "JUVIKS"
            logo_b64 = None
    except:
        empresa_nome = "JUVIKS"
        logo_b64 = None

    # Header com estilo Card Premium para o Cliente
    logo_src = logo_b64 if (logo_b64 and logo_b64.startswith("data:")) else (f"data:image/png;base64,{logo_b64}" if logo_b64 else "")
    logo_html = f'<div style="text-align:center;"><img src="{logo_src}" style="max-height:90px; margin-bottom:20px;" /></div>' if logo_src else ""
    
    header_html = f"""<div class="client-header" style="text-align:center; padding: 10px 20px 30px;">
{logo_html}
<div style="font-size:0.8rem; color:#94a3b8; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;">Documento enviado por</div>
<div style="font-size:1.8rem; font-weight:900; color:#ffffff; margin-bottom:25px; line-height:1.2;">{empresa_nome}</div>
<div style="background: linear-gradient(90deg, #3b82f6, #2dd4bf); height: 2px; width: 60px; margin: 0 auto 25px;"></div>
<h1 style="font-size:1.3rem; font-weight:600; margin:0; color:#f8fafc;">✍️ Assinatura Digital Eletrônica</h1>
<p style="color:#94a3b8; font-size:1rem; margin-top:10px; margin-bottom:0;">Portal de Assinaturas Jurídicas — Válido Legalmente</p>
</div>"""
    st.markdown(header_html, unsafe_allow_html=True)

    status = doc["status"]

    if status == "completed":
        st.success("✅ Este documento já foi **completamente assinado** por ambas as partes.")
        pdf_path = os.path.join(SIGNED_DIR, f"completed_{doc['filename']}")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Baixar PDF Assinado", f.read(), f"{doc['original_filename']}", use_container_width=True)
        st.stop()

    if status == "rejected":
        st.error("❌ Este documento foi **recusado**.")
        st.stop()

    if status == "client_signed":
        st.info("✅ Você já assinou este documento. Aguardando validação da empresa.")
        st.stop()

    # Mostrar info do documento
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-row"><span class="info-key">Arquivo</span><span class="info-val">{doc['original_filename']}</span></div>
            <div class="info-row"><span class="info-key">Data Envio</span><span class="info-val">{doc['created_at']}</span></div>
            <div class="info-row"><span class="info-key">Status</span><span class="info-val">Aguardando sua assinatura</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-row"><span class="info-key">ID do Documento</span><span class="info-val" style="font-family:monospace;font-size:.75rem">{doc['id'][:16]}...</span></div>
            <div class="info-row"><span class="info-key">Validade</span><span class="info-val">Assinatura Eletrônica</span></div>
            <div class="info-row"><span class="info-key">Protocolo</span><span class="info-val">ASSINA HD 1.0</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Mostrar PDF
    pdf_path_empresa = os.path.join(SIGNED_DIR, f"empresa_{doc['filename']}")
    pdf_path_original = os.path.join(UPLOADS_DIR, doc["filename"])
    pdf_path = pdf_path_empresa if os.path.exists(pdf_path_empresa) else pdf_path_original

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="border:1px solid #252840;border-radius:12px;overflow:hidden;margin-bottom:20px;">
            <iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="500" style="border:none;display:block;"></iframe>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Arquivo PDF não encontrado no servidor.")

    st.subheader("✍️ Sua Assinatura")
    st.caption("Escolha como deseja assinar este documento:")

    metodo = st.radio("Forma de Assinatura:", ["✏️ Desenhar", "⌨️ Digitar Nome", "🖼️ Upload de Imagem"], horizontal=True, key="metodo_sig")
    sig_b64 = None
    
    if metodo == "✏️ Desenhar":
        canvas_result = st_canvas(fill_color="rgba(0,0,0,0)", stroke_width=3, stroke_color="#1e40af", background_color="#ffffff", height=140, drawing_mode="freedraw", key="client_sig_canvas")
        if canvas_result and canvas_result.image_data is not None: sig_b64 = canvas_to_base64(canvas_result)

    elif metodo == "🖼️ Upload de Imagem":
        sig_file = st.file_uploader("Imagem da assinatura (PNG transparente):", type=["png","jpg","jpeg"], key="client_sig_file")
        if sig_file:
            sig_b64 = file_to_base64(sig_file)
            st.image(sig_file, width=200)

    elif metodo == "⌨️ Digitar Nome":
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Great+Vibes&family=Alex+Brush&display=swap');
            </style>
        """, unsafe_allow_html=True)
        
        sugestao_nome = doc['client_name'] or ""
        typed_name = st.text_input("Digite seu Nome Completo:", value=sugestao_nome, key="ty_name")
        
        font_choices = {
            "Estilo Elegante": ("Dancing Script", "segoesc.ttf"),
            "Estilo Cursivo": ("Great Vibes", "vladimir.ttf"),
            "Estilo Artístico": ("Alex Brush", "itckrist.ttf")
        }
        
        sel_font_label = st.radio("Escolha o Estilo (Fonte):", list(font_choices.keys()), horizontal=True)
        css_font, ttf_font = font_choices[sel_font_label]
        
        st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 25px; text-align: center; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-family: '{css_font}', cursive; font-size: 3rem; color: #1e3a8a; line-height: 1;">
                    {typed_name if typed_name else 'Sua Assinatura'}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if typed_name:
            sig_b64 = text_to_signature_base64(typed_name, font_name=ttf_font)

    st.write("")
    # Checkbox de aceite legal
    aceite = st.checkbox("✅ Li e concordo com o conteúdo do documento acima e autorizo minha assinatura eletrônica com validade jurídica conforme MP 2.200-2/2001.")

    col_a, col_r = st.columns([2,1])
    with col_a:
        assinar = st.button("✍️ CONFIRMAR ASSINATURA", type="primary", use_container_width=True, disabled=not aceite)
    with col_r:
        recusar = st.button("❌ Recusar Documento", use_container_width=True)

    if recusar:
        conn = db_conn()
        conn.execute("UPDATE documents SET status='rejected' WHERE id=?", (sign_id,))
        conn.commit(); conn.close()
        st.error("Documento recusado. Esta ação foi registrada.")
        st.rerun()

    if assinar:
        if not sig_b64:
            st.error("⚠️ Por favor, desenhe ou faça upload da sua assinatura.")
        else:
            input_pdf  = pdf_path
            output_pdf = os.path.join(SIGNED_DIR, f"completed_{doc['filename']}")
            sign_data = {
                "name": f"Cliente ({doc['whatsapp_number']})",
                "id": sign_id,
                "original_filename": doc["original_filename"],
                "ip": "Web-Streamlit",
                "location": "Assinado via plataforma online",
                "mac_address": f"UID-{hashlib.sha1(sign_id.encode()).hexdigest()[:8].upper()}",
                "visual_signature": sig_b64
            }
            try:
                sign_pdf(input_pdf, output_pdf, sign_data, "CLIENT")
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = db_conn()
                conn.execute("""
                    UPDATE documents SET status='completed',
                    client_ip='Web-Streamlit', client_location='Online',
                    client_signature_time=? WHERE id=?
                """, (now, sign_id))
                conn.commit(); conn.close()
                st.success("🎉 **Assinatura registrada com sucesso!** O documento foi completamente assinado por ambas as partes.")
                
                # ---- AVISO INTERNO PARA A ADMINISTRAÇÃO DIRETO NO CELULAR DA API ----
                try:
                    # O row_factory do SQLite não tem .get(), precisamos converter para dict
                    dict_doc = dict(doc)
                    url_self = "http://127.0.0.1:3000/send-self"
                    msg_admin = f"✅ *CONTRATO ASSINADO!*\n\n*Orçamento N°:* {dict_doc.get('numero_pedido') or '--'}\n*Cliente:* {dict_doc.get('client_name') or 'N/A'}"
                    requests.post(url_self, json={"message": msg_admin}, timeout=5)
                except Exception as e:
                    pass # Oculta falhas do lado do cliente
                
                st.balloons()
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao assinar: {e}")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  PAINEL ADMIN (requer autenticação)
# ══════════════════════════════════════════════════════════════════════════════
from database import buscar_dados
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo
from TEMAS.moderno import apply_modern_style

nome_empresa, logo_src = obter_dados_empresa()
st.set_page_config(
    page_title=f"Assinaturas | {nome_empresa}",
    layout="wide", page_icon="✍️"
)

# Aplica o estilo global moderno com logo
apply_modern_style(logo_url=logo_src, nome_empresa=nome_empresa)

verificar_autenticacao()
from utils.auth_manager import verificar_nivel_acesso
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR"])
verificar_permissao_modulo("Assinaturas")

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.title("✍️ Assinaturas Digitais")
st.divider()

# ─── ABAS ADMIN ───────────────────────────────────────────────────────────────
tab_dash, tab_envio, tab_fila, tab_ok = st.tabs([
    "📊 Dashboard", "📤 Enviar Documento",
    "📋 Fila de Assinatura", "✅ Concluídos"
])

# ══════════════ TAB DASHBOARD ══════════════
with tab_dash:
    verificar_permissao_modulo("Assinaturas - Dashboard/Logs")
    total   = count_docs()
    pend_emp = count_docs("pending_empresa")
    pend_cli = count_docs("pending_client")
    pend_total = pend_emp + pend_cli + count_docs("pending") # Including legacy
    csigned = count_docs("client_signed")
    done    = count_docs("completed")
    reject  = count_docs("rejected")

    st.markdown(f"""
    <div style="display: flex; gap: 1rem; width: 100%; flex-wrap: wrap; margin-bottom: 2rem;">
        <div style="flex: 1; min-width: 120px; background: rgba(2,8,23,0.5); border: 1px solid rgba(56,189,248,.2); border-radius: 8px; padding: 1.2rem 1rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #a78bfa; font-family: 'JetBrains Mono', monospace; line-height: 1;">{total}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.6rem;">Total</div>
        </div>
        <div style="flex: 1; min-width: 120px; background: rgba(2,8,23,0.5); border: 1px solid rgba(56,189,248,.2); border-radius: 8px; padding: 1.2rem 1rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #fbbf24; font-family: 'JetBrains Mono', monospace; line-height: 1;">{pend_total}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.6rem;">Aguardando</div>
        </div>
        <div style="flex: 1; min-width: 120px; background: rgba(2,8,23,0.5); border: 1px solid rgba(56,189,248,.2); border-radius: 8px; padding: 1.2rem 1rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #38bdf8; font-family: 'JetBrains Mono', monospace; line-height: 1;">{csigned}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.6rem;">Cliente Assinou</div>
        </div>
        <div style="flex: 1; min-width: 120px; background: rgba(2,8,23,0.5); border: 1px solid rgba(56,189,248,.2); border-radius: 8px; padding: 1.2rem 1rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #22c55e; font-family: 'JetBrains Mono', monospace; line-height: 1;">{done}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.6rem;">Concluídos</div>
        </div>
        <div style="flex: 1; min-width: 120px; background: rgba(2,8,23,0.5); border: 1px solid rgba(56,189,248,.2); border-radius: 8px; padding: 1.2rem 1rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #ef4444; font-family: 'JetBrains Mono', monospace; line-height: 1;">{reject}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.6rem;">Recusados</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📋 Documentos Recentes")
    docs = get_docs()
    if not docs:
        st.info("Nenhum documento cadastrado ainda.")
    else:
        for doc in docs[:10]:
            s = doc["status"]
            badge_map = {
                "pending":      ('<span class="badge badge-pending">🕐 Aguardando</span>', "#fbbf24"),
                "client_signed":('<span class="badge badge-signed">✅ Cliente Assinou</span>', "#3b82f6"),
                "completed":    ('<span class="badge badge-complete">🏆 Concluído</span>', "#22c55e"),
                "rejected":     ('<span class="badge badge-rejected">❌ Recusado</span>', "#ef4444"),
            }
            badge, color = badge_map.get(s, ('<span class="badge">?</span>', "#888"))
            # Info do cliente formatada
            doc_dict = dict(doc)
            label_cliente = f"**{doc_dict.get('razao_social') or 'N/A'}** ({doc_dict.get('client_name') or 'N/A'})"
            st.markdown(f"""
            <div class="doc-card" style="border-left:4px solid {color}; padding: 12px; margin-bottom: 10px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start">
                    <div style="flex: 1;">
                        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: .75rem; background: #334155; padding: 2px 8px; border-radius: 4px; color: #94a3b8; font-weight: 600;">Pedido: {doc_dict.get('numero_pedido') or '—'}</span>
                            {badge}
                        </div>
                        <div style="font-size: 1rem; font-weight: 700; color: #f8fafc; margin-bottom: 2px;">{label_cliente}</div>
                        <div style="font-size: .85rem; font-weight: 500; color: #94a3b8;">
                            📄 {doc['original_filename']}
                        </div>
                        <div style="font-size: .78rem; color: #64748b; margin-top: 6px; display: flex; align-items: center; gap: 12px;">
                            <span>📱 {doc['whatsapp_number']}</span>
                            <span>🕒 {doc['created_at'] or '—'}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════ TAB ENVIO ══════════════
with tab_envio:
    verificar_permissao_modulo("Assinaturas - Enviar Convites")
    col_form, col_prev = st.columns([1, 1])

    with col_form:
        st.subheader("📤 Novo Documento")
        with st.form("form_upload", clear_on_submit=True):
            pdf_file = st.file_uploader("Arquivo PDF", type=["pdf"])
            client_name = st.text_input("Nome do Cliente", placeholder="Ex: João da Silva")
            razao_social = st.text_input("Razão Social do Cliente / Empresa", placeholder="Ex: João da Silva ME")
            numero_pedido = st.text_input("Número do Pedido / Orçamento", placeholder="Ex: 12345")
            whatsapp = st.text_input("WhatsApp do Cliente (com DDI)", placeholder="Ex: 5511999999999")
            submitted = st.form_submit_button("🚀 Enviar para Fila de Assinatura", type="primary", use_container_width=True)

        if submitted:
            if not pdf_file or not whatsapp.strip() or not razao_social.strip() or not client_name.strip():
                st.error("Preencha todos os campos, incluindo Razão Social e Nome do Cliente.")
            else:
                wapp = whatsapp.strip().replace(" ","").replace("-","").replace("(","").replace(")","")
                doc_id = str(uuid.uuid4())
                original_name = pdf_file.name
                filename = f"{doc_id}_{original_name}"
                filepath = os.path.join(UPLOADS_DIR, filename)

                with open(filepath, "wb") as f:
                    f.write(pdf_file.getvalue())

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = db_conn()
                conn.execute("""
                    INSERT INTO documents (id, original_filename, filename, whatsapp_number, created_at, client_name, razao_social, numero_pedido, status)
                    VALUES (?,?,?,?,?,?,?,?, 'pending_empresa')
                """, (doc_id, original_name, filename, wapp, now, client_name, razao_social, numero_pedido))
                conn.commit(); conn.close()

                st.success("✅ Documento registrado! Vá para a aba 'Fila de Assinatura' para você assinar antes do cliente.")
                st.session_state["last_upload"] = pdf_file.getvalue()

    with col_prev:
        st.subheader("👁️ Pré-visualização")
        if "last_upload" in st.session_state:
            b64 = base64.b64encode(st.session_state["last_upload"]).decode()
            st.markdown(f"""
            <iframe src="data:application/pdf;base64,{b64}" width="100%" height="500"
            style="border:1px solid #252840;border-radius:12px;display:block;"></iframe>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:500px;border:1px dashed #252840;border-radius:12px;
            display:flex;align-items:center;justify-content:center;color:#475569;flex-direction:column;gap:12px">
                <div style="font-size:3rem;">📄</div>
                <div>O PDF aparecerá aqui após o upload</div>
            </div>""", unsafe_allow_html=True)

# ══════════════ TAB FILA ══════════════
with tab_fila:
    st.subheader("📋 Fila de Assinatura")

    docs_ativos = [d for d in get_docs() if d["status"] in ("pending", "pending_empresa", "pending_client")]

    if not docs_ativos:
        st.info("✅ Nenhum documento na fila no momento.")
    else:
        for doc in docs_ativos:
            s      = doc["status"]
            
            # Treat legacy 'pending' as 'pending_empresa' or 'pending_client' depending on workflow
            # Since workflow changed to company first, 'pending' will be treated as 'pending_empresa'
            if s == "pending": s = "pending_empresa"
                
            cor    = "#fbbf24" if s == "pending_empresa" else "#3b82f6"
            label  = "AGUARDANDO SUA ASSINATURA (EMPRESA)" if s == "pending_empresa" else "AGUARDANDO ASSINATURA DO CLIENTE"
            link   = link_cliente(doc["id"])
            wapp   = doc["whatsapp_number"]
            
            # Busca o Numero Oficial da Empresa para o Rodapé via helper centralizado
            try:
                from database import buscar_dados as _bd
                _df_q = _bd("SELECT empresa_whatsapp FROM config LIMIT 1")
                num_oficial = _df_q.iloc[0]['empresa_whatsapp'] if not _df_q.empty else ""
            except:
                num_oficial = ""

            # Mensagem do WhatsApp customizada
            doc_dict = dict(doc)
            razao = doc_dict.get("razao_social") or "Não informada"
            cli = doc_dict.get("client_name") or "Cliente"
            ped = doc_dict.get("numero_pedido") or "Avulso"
            import urllib.parse
            # Mensagem focada para o cliente
            rodape_oficial = f"\n\n*Central de Atendimento:* {num_oficial}" if num_oficial else ""
            texto_msg = f"Olá, *{cli or 'Sr(a)'}*!\n\nSegue o link oficial para a assinatura eletrônica do seu documento.\n\n*Razão Social:* {razao}\n*Cliente:* {cli}\n*Pedido:* {ped}\n\n*Link para Assinar:* {link}\n\nEstamos no aguardo.{rodape_oficial}\nAtenciosamente."

            # Limpeza final do número (apenas números)
            wapp_clean = "".join(filter(str.isdigit, str(wapp)))
            
            # Gerar links (App vs Web)
            # wa.me é o redirecionador oficial mais estável e curto
            wpp_app_link = f"whatsapp://send?phone={wapp_clean}&text={urllib.parse.quote(texto_msg)}"
            wpp_web_link = f"https://wa.me/{wapp_clean}?text={urllib.parse.quote(texto_msg)}"

            with st.container(border=True):
                c1, c2 = st.columns([3,1])
                with c1:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                        <span class="badge" style="background:rgba({
                            '251,191,36' if s=='pending_empresa' else '59,130,246'
                        },.1);border:1px solid {cor};color:{cor}">{label}</span>
                    </div>
                    <div style="font-size:1.1rem;font-weight:600;color:#f8fafc">{cli}</div>
                    <strong style="color:#94a3b8;font-size:0.9rem">{doc['original_filename']}</strong>
                    <div style="font-size:.8rem;color:#64748b;margin-top:4px">
                        📱 {wapp} &nbsp;|&nbsp; 📝 Pedido: {ped} &nbsp;|&nbsp; 🕒 {doc['created_at'] or '—'}
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("❌ Apagar", key=f"del_{doc['id']}", use_container_width=True):
                        for p in [
                            os.path.join(UPLOADS_DIR, doc["filename"]),
                            os.path.join(SIGNED_DIR, f"empresa_{doc['filename']}"),
                            os.path.join(SIGNED_DIR, f"client_{doc['filename']}"), # fallback legacy
                            os.path.join(SIGNED_DIR, f"completed_{doc['filename']}")
                        ]:
                            try:
                                if os.path.exists(p): os.remove(p)
                            except: pass
                        conn = db_conn()
                        conn.execute("DELETE FROM documents WHERE id=?", (doc["id"],))
                        conn.commit(); conn.close()
                        st.rerun()

                # Ações por status
                if s == "pending_empresa":
                    st.warning("⚠️ Você (Empresa) precisa assinar este documento ANTES de liberar o link para o cliente.")

                    # Accordion para assinar
                    with st.expander("✍️ ASSINAR AGORA (Empresa)", expanded=True):
                        st.caption("Desenhe sua assinatura ou faça upload de imagem:")
                        tab_d, tab_u = st.tabs(["✏️ Desenhar", "🖼️ Upload"])

                        adm_sig = None
                        with tab_d:
                            adm_canvas = st_canvas(
                                fill_color="rgba(0,0,0,0)",
                                stroke_width=3,
                                stroke_color="#15803d",
                                background_color="#ffffff",
                                height=130,
                                drawing_mode="freedraw",
                                key=f"adm_canvas_{doc['id']}",
                            )
                            adm_sig = canvas_to_base64(adm_canvas)

                        with tab_u:
                            adm_file = st.file_uploader("Imagem assinatura empresa:", type=["png","jpg","jpeg"], key=f"adm_file_{doc['id']}")
                            if adm_file:
                                adm_sig = file_to_base64(adm_file)
                                st.image(adm_file, width=180)

                        if st.button("🏁 ASSINAR E LIBERAR LINK", key=f"fin_{doc['id']}", type="primary", use_container_width=True):
                            if not adm_sig:
                                st.error("Você precisa desenhar ou enviar a imagem da assinatura.")
                            else:
                                input_pdf  = os.path.join(UPLOADS_DIR, doc["filename"])
                                output_pdf = os.path.join(SIGNED_DIR, f"empresa_{doc['filename']}")
                                sign_data = {
                                    "name": "Administrador / Empresa",
                                    "id": doc["id"],
                                    "original_filename": doc["original_filename"],
                                    "ip": "Admin-Streamlit",
                                    "location": "Sede Administrativa",
                                    "mac_address": f"ADM-{os.cpu_count() or 0}",
                                    "visual_signature": adm_sig
                                }
                                try:
                                    sign_pdf(input_pdf, output_pdf, sign_data, "SENDER")
                                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    conn = db_conn()
                                    conn.execute("""
                                        UPDATE documents SET status='pending_client',
                                        sender_ip='Admin-Streamlit', sender_signature_time=?
                                        WHERE id=?
                                    """, (now, doc["id"]))
                                    conn.commit(); conn.close()
                                    st.success("✅ Assinado com sucesso! Link liberado.")
                                    # --- AUTOMAÇÃO DE ENVIO ---
                                    ok, msg_api = enviar_whatsapp_api(doc['whatsapp_number'], texto_msg)
                                    if ok:
                                        st.info("📨 Link enviado automaticamente para o WhatsApp do cliente!")
                                    # --------------------------
                                    time.sleep(1.5)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao assinar: {e}")

                elif s == "pending_client":
                    st.success("✅ A empresa já assinou. O arquivo enviado ao cliente será o documento oficial com sua assinatura.")
                    
                    # Detalhes do Gateway e Remetente
                    # Utiliza o helper centralizado para evitar erros de caminho
                    from database import buscar_dados as _bd
                    df_api = _bd("SELECT wpp_api_url, wpp_instance, empresa_whatsapp FROM config LIMIT 1")
                    conf_api = df_api.iloc[0].to_dict() if not df_api.empty else None
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:15px; border-left: 4px solid #00ff00;">
                        <div style="font-size:0.7rem; color:#888;">REMETENTE OFICIAL</div>
                        <div style="font-weight:bold; color:#00ff00;">📱 {conf_api['empresa_whatsapp'] if conf_api else 'Não configurado'}</div>
                        <div style="font-size:0.7rem; color:#888; margin-top:5px;">DESTINATÁRIO (CLIENTE)</div>
                        <div style="font-weight:bold;">👤 {wapp}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    ca, cb = st.columns(2)
                    if ca.button("🚀 Envio Direto (Motor)", key=f"re_auto_{doc['id']}", use_container_width=True, help="Envia sozinho pelo seu WhatsApp logado no QR Code"):
                         ok, msg = enviar_whatsapp_api(wapp, texto_msg)
                         if ok: st.success("✅ Mensagem enviada via Motor!")
                         else: st.error(f"Erro Motor: {msg}")
                    else:
                         # Regra de Envio Manual (App vs Web)
                         escolha = ca.radio("Regra de Envio:", ["Aplicativo (Fixo)", "Navegador Web"], key=f"rule_{doc['id']}", horizontal=True, label_visibility="collapsed")
                         if escolha == "Aplicativo (Fixo)":
                             ca.link_button("📲 Enviar via App Windows", wpp_app_link, use_container_width=True, type="primary", help="Abre o WhatsApp instalado no seu computador")
                         else:
                             ca.link_button("📲 Abrir no Navegador", wpp_web_link, use_container_width=True, type="secondary")
                    
                    with cb.expander("📋 Link Manual"):
                        st.code(link, language=None)

# ══════════════ TAB CONCLUÍDOS ══════════════
with tab_ok:
    st.subheader("✅ Documentos Finalizados")

    docs_ok = get_docs("completed")
    docs_rej = get_docs("rejected")

    c_ok, c_rej = st.columns(2)

    with c_ok:
        st.markdown("#### 🏆 Assinados Bilateralmente")
        if not docs_ok:
            st.info("Nenhum até agora.")
        for doc in docs_ok:
            with st.container(border=True):
                st.markdown(f"""
                <div style="font-size:1.05rem;font-weight:600;color:#f8fafc">{doc['client_name'] or 'Cliente não identificado'}</div>
                <strong style="color:#94a3b8;font-size:0.85rem">{doc['original_filename']}</strong>
                <div style="font-size:.78rem;color:#64748b;margin-top:4px">
                    📱 {doc['whatsapp_number']}<br>
                    ✍️ Cliente: {doc['client_signature_time'] or '—'}<br>
                    🏢 Empresa: {doc['sender_signature_time'] or '—'}
                </div>""", unsafe_allow_html=True)
                pdf_path = os.path.join(SIGNED_DIR, f"completed_{doc['filename']}")
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "📥 Baixar PDF Final",
                            f.read(),
                            f"Assinado_{doc['original_filename']}",
                            use_container_width=True,
                            key=f"dl_{doc['id']}"
                        )
                if st.button("🗑️ Apagar", key=f"del_ok_{doc['id']}", use_container_width=True):
                    for p in [
                        os.path.join(UPLOADS_DIR, doc["filename"]),
                        os.path.join(SIGNED_DIR, f"client_{doc['filename']}"),
                        os.path.join(SIGNED_DIR, f"completed_{doc['filename']}")
                    ]:
                        try:
                            if os.path.exists(p): os.remove(p)
                        except: pass
                    conn = db_conn()
                    conn.execute("DELETE FROM documents WHERE id=?", (doc["id"],))
                    conn.commit(); conn.close()
                    st.rerun()

    with c_rej:
        st.markdown("#### ❌ Recusados")
        if not docs_rej:
            st.info("Nenhum recusado.")
        for doc in docs_rej:
            with st.container(border=True):
                st.markdown(f"""
                <div style="border-left:3px solid #ef4444;padding-left:12px">
                <div style="font-weight:600">{doc['client_name'] or 'Cliente não identificado'}</div>
                <strong style="font-size:0.85rem;color:#94a3b8">{doc['original_filename']}</strong>
                <div style="font-size:.78rem;color:#64748b;margin-top:4px">📱 {doc['whatsapp_number']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button("🗑️ Remover", key=f"del_rej_{doc['id']}", use_container_width=True):
                    for p in [
                        os.path.join(UPLOADS_DIR, doc["filename"]),
                        os.path.join(SIGNED_DIR, f"client_{doc['filename']}")
                    ]:
                        try:
                            if os.path.exists(p): os.remove(p)
                        except: pass
                    conn = db_conn()
                    conn.execute("DELETE FROM documents WHERE id=?", (doc["id"],))
                    conn.commit(); conn.close()
                    st.rerun()
