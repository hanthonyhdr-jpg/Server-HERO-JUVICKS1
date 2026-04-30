import streamlit as st
import os, re, shutil, json
from datetime import datetime

st.set_page_config(
    page_title="Editor de Tema — JUVIKS07",
    layout="wide", page_icon="🎨",
    initial_sidebar_state="expanded"
)

# ─── PATHS ─────────────────────────────────────────────────────────────────────
THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
TEMA_FILE  = os.path.join(THIS_DIR, "..", "PY", "TEMAS", "moderno.py")
BACKUP_DIR = os.path.join(THIS_DIR, "backups")
PRESET_DIR = os.path.join(THIS_DIR, "presets")
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(PRESET_DIR, exist_ok=True)

# ─── CSS DO EDITOR ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
*, html, body { font-family: 'Space Grotesk', sans-serif !important; }
.stApp { background: radial-gradient(135deg, #0a0a1a 0%, #000008 100%); color: #e2e8f0; }
[data-testid="stSidebar"] { background: rgba(5,5,20,0.97) !important; border-right: 1px solid rgba(255,255,255,0.06); }
.stButton > button { border-radius:10px !important; font-weight:600 !important; transition:all .2s !important; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div > div { background: rgba(10,10,30,0.8) !important; border:1px solid rgba(255,255,255,0.1) !important; border-radius:8px !important; color:#e2e8f0 !important; }
.section-hdr { font-size:.7rem; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:#64748b; margin:18px 0 6px; padding-bottom:4px; border-bottom:1px solid rgba(255,255,255,0.06); }
.preset-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:14px; cursor:pointer; transition:all .2s; margin-bottom:8px; }
.preset-card:hover { border-color:#7c3aed; transform:translateY(-2px); }
.color-preview { display:inline-block; width:18px; height:18px; border-radius:4px; border:1px solid rgba(255,255,255,0.2); vertical-align:middle; margin-right:6px; }
#MainMenu,footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def load_tema():
    with open(TEMA_FILE, 'r', encoding='utf-8') as f: return f.read()

def save_tema(content, note=""):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = f"_{note}" if note else ""
    shutil.copy2(TEMA_FILE, os.path.join(BACKUP_DIR, f"backup{label}_{ts}.py"))
    with open(TEMA_FILE, 'w', encoding='utf-8') as f: f.write(content)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def extract_first_hex(text, fallback="#000000"):
    m = re.findall(r'#([0-9a-fA-F]{6})', text)
    return f"#{m[0]}" if m else fallback

# Funções auxiliares sempre geradas no final do moderno.py
_TAIL_FUNCTIONS = '''

def apply_signature_management_style():
    """Aplica CSS para a gestão de assinaturas no painel admin."""
    st.markdown("""
        <style>
        .stat-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 28px; }
        .stat-card { background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 20px 16px; text-align: center; transition: all .25s ease; backdrop-filter: blur(10px); }
        .stat-card:hover { transform: translateY(-3px); border-color: #64748b; }
        .stat-num { font-size: 2.1rem; font-weight: 800; color: #0ea5e9; }
        .stat-label { font-size: .75rem; color: #94a3b8; margin-top: 4px; font-weight: 600; text-transform: uppercase; }
        .doc-card { background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 16px 18px; margin-bottom: 12px; transition: border-color .2s; }
        .doc-card:hover { border-color: #0ea5e9; }
        .badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: .7rem; font-weight: 700; text-transform: uppercase; }
        .badge-pending  { background: rgba(251,191,36,.1);  border: 1px solid #fbbf24; color: #fbbf24; }
        .badge-signed   { background: rgba(59,130,246,.1);  border: 1px solid #3b82f6; color: #3b82f6; }
        .badge-complete { background: rgba(34,197,94,.1);   border: 1px solid #22c55e; color: #22c55e; }
        .badge-rejected { background: rgba(239,68,68,.1);   border: 1px solid #ef4444; color: #ef4444; }
        </style>
    """, unsafe_allow_html=True)


def get_signature_client_style():
    """Retorna o CSS para a pagina publica de assinatura do cliente."""
    return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        html, body, [class*="st-"] { font-family: 'Outfit', sans-serif; }
        .stApp { background: radial-gradient(circle at 50% 50%, #0f172a 0%, #020617 100%); color: #f1f5f9; }
        header[data-testid="stHeader"] { background: transparent !important; }
        #MainMenu, footer { visibility: hidden; }
        .stAppDeployButton, .stDeployButton { display: none !important; }
        .client-header { background: linear-gradient(135deg, #0ea5e9, #6366f1); padding: 32px; border-radius: 20px; text-align: center; margin-bottom: 24px; }
        .client-header h1 { color: white !important; font-size: 1.8rem; font-weight: 700; margin: 0; }
        .client-header p  { color: rgba(255,255,255,.9); margin: 8px 0 0; }
        .info-box { background: rgba(30,41,59,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 16px; backdrop-filter: blur(10px); }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: .85rem; }
        .info-row:last-child { border-bottom: none; }
        .info-key { color: #94a3b8; font-weight: 600; }
        .info-val { color: #f1f5f9; }
        </style>
    """


def get_login_style():
    """Retorna o CSS para a tela de login."""
    return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden; }
        .stApp { background: radial-gradient(circle at 20% 20%, #1e293b 0%, #020617 100%) !important; font-family: 'Outfit', sans-serif !important; }
        .block-container { padding-top: 0 !important; max-width: 100% !important; }
        .login-card { background: rgba(30,41,59,0.4); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 40px; }
        .stTextInput input { background-color: rgba(15,23,42,0.6) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; color: #f8fafc !important; padding: 12px 16px !important; }
        .stButton > button { background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important; color: white !important; border-radius: 12px !important; font-size: 16px !important; font-weight: 600 !important; padding: 14px !important; width: 100% !important; }
        .stAppDeployButton, .stDeployButton { display: none !important; }
        </style>
    """


def apply_license_style():
    """Design 100% IDENTICO ao modelo HTML juviks_activation.html."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
        :root { --bg: #07080d; --surface: #0e1018; --border: rgba(255,255,255,0.07); --border-glow: rgba(99,197,255,0.3); --accent: #63c5ff; --accent2: #a78bfa; --text: #e8eaf0; --muted: #5a5f72; --danger: #ff5f6d; --success: #4ade80; --gold: #f5c842; }
        .ambient { position: fixed; border-radius: 50%; filter: blur(120px); pointer-events: none; z-index: 0; }
        .ambient-1 { width: 600px; height: 600px; background: radial-gradient(circle, rgba(99,197,255,0.07) 0%, transparent 70%); top: -100px; left: -100px; animation: drift1 12s ease-in-out infinite alternate; }
        .ambient-2 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(167,139,250,0.06) 0%, transparent 70%); bottom: -80px; right: -80px; animation: drift2 15s ease-in-out infinite alternate; }
        @keyframes drift1 { to { transform: translate(60px, 40px); } }
        @keyframes drift2 { to { transform: translate(-40px, -60px); } }
        .stApp { background: var(--bg) !important; font-family: 'DM Mono', monospace !important; color: var(--text) !important; overflow: hidden !important; }
        .stApp::before { content: ''; position: fixed; inset: 0; background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"); pointer-events: none; z-index: 1; opacity: 0.35; }
        .block-container { max-width: 520px !important; padding: 0 !important; margin: auto !important; height: 100vh !important; display: flex !important; align-items: center !important; justify-content: center !important; z-index: 1000; }
        .card { width: 100%; background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.015) 100%); border: 1px solid var(--border); border-radius: 20px; padding: 48px 44px; backdrop-filter: blur(20px); box-shadow: 0 40px 80px rgba(0,0,0,0.6); animation: fadeUp 0.6s both; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
        .header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 36px; }
        .logo-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(99,197,255,0.08); border: 1px solid rgba(99,197,255,0.2); border-radius: 6px; padding: 5px 12px; margin-bottom: 14px; }
        .title { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800; color: var(--text); }
        .title span { color: var(--accent); }
        .status-chip { display: flex; align-items: center; gap: 6px; background: rgba(255,95,109,0.1); border: 1px solid rgba(255,95,109,0.25); border-radius: 20px; padding: 6px 14px; color: var(--danger); font-size: 11px; }
        .info-block { background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 10px; padding: 16px 18px; margin-bottom: 28px; }
        .copy-btn { background: none; border: 1px solid var(--border); border-radius: 6px; color: var(--muted); cursor: pointer; padding: 4px 10px; font-size: 10px; }
        .copy-btn.copied { border-color: var(--success); color: var(--success); }
        .segmented-row { display: flex; align-items: center; gap: 6px; margin-bottom: 12px; }
        .segmented-row .stTextInput div div input { background: rgba(255,255,255,0.03) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; text-align: center !important; font-family: 'DM Mono', monospace !important; }
        .stButton > button { width: 100% !important; background: linear-gradient(135deg, #63c5ff 0%, #a78bfa 100%) !important; border: none !important; border-radius: 12px !important; color: #07080d !important; font-weight: 700 !important; height: 56px !important; }
        .footer { margin-top: 32px; padding-top: 22px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); }
        </style>
    """, unsafe_allow_html=True)
'''

def gen_theme(cfg):
    """Gera o conteúdo completo do moderno.py a partir de um dicionário de tokens.
    Gera arquivo SEM f-string no CSS principal — chaves simples { } funcionam livremente."""
    bg1     = cfg['bg1']
    bg2     = cfg['bg2']
    accent  = cfg['accent']
    accent2 = cfg['accent2']
    text1   = cfg['text1']
    text2   = cfg['text2']
    card_bg = cfg['card_bg']
    sidebar = cfg['sidebar']
    font    = cfg['font']
    r_card  = cfg['r_card']
    r_btn   = cfg['r_btn']
    r_inp   = cfg['r_inp']
    blur_sb = cfg['blur_sb']
    blur_cd = cfg['blur_cd']
    opacity_card = cfg['opacity_card']

    font_url  = font.replace(' ', '+')
    bg1_r, bg1_g, bg1_b = hex_to_rgb(bg1)
    acc_r, acc_g, acc_b = hex_to_rgb(accent)
    crd_r, crd_g, crd_b = hex_to_rgb(card_bg)
    sdb_r, sdb_g, sdb_b = hex_to_rgb(sidebar)

    # CSS gerado como string Python comum — SEM f-string, chaves livres
    css = (
        "    <style>\n"
        "    /* ═══════════════════════════════════════\n"
        "       1. FONTE GLOBAL\n"
        "       ═══════════════════════════════════════ */\n"
        f"    @import url('https://fonts.googleapis.com/css2?family={font_url}:wght@300;400;600&display=swap');\n\n"
        "    html, body, [class*=\"st-\"]:not(i):not(span):not([data-testid=\"stIcon\"]) {\n"
        f"        font-family: '{font}', sans-serif;\n"
        "    }\n"
        "    [data-testid=\"stIcon\"], i, span[data-testid=\"stIcon\"] {\n"
        "        font-family: \"Material Symbols Outlined\", \"Material Icons\", \"Segoe UI Symbol\", sans-serif !important;\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       2. FUNDO PRINCIPAL (App Background)\n"
        "       ═══════════════════════════════════════ */\n"
        "    .stApp {\n"
        f"        background: radial-gradient(circle at 50% 50%, {bg1} 0%, {bg2} 100%);\n"
        f"        color: {text1};                /* Cor do texto global */\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       3. SIDEBAR — Cores Independentes\n"
        "       ═══════════════════════════════════════ */\n\n"
        "    /* 3A. Fundo da Sidebar */\n"
        "    [data-testid=\"stSidebar\"] {\n"
        f"        background-color: rgba({sdb_r}, {sdb_g}, {sdb_b}, 0.95) !important;   /* ← FUNDO SIDEBAR */\n"
        f"        backdrop-filter: blur({blur_sb}px);\n"
        "        border-right: 1px solid rgba(255, 255, 255, 0.07);   /* ← BORDA SIDEBAR */\n"
        "    }\n"
        "    [data-testid=\"stSidebarNav\"] { padding-top: 1.5rem; }\n\n"
        "    /* 3B. Texto dos itens de navegação na Sidebar */\n"
        "    [data-testid=\"stSidebar\"] p,\n"
        "    [data-testid=\"stSidebar\"] label,\n"
        "    [data-testid=\"stSidebar\"] span,\n"
        "    [data-testid=\"stSidebar\"] .stMarkdown p {\n"
        f"        color: {text2} !important;    /* ← TEXTO SIDEBAR */\n"
        "    }\n\n"
        "    /* 3C. Item ativo / selecionado na Sidebar */\n"
        "    [data-testid=\"stSidebar\"] [aria-selected=\"true\"],\n"
        "    [data-testid=\"stSidebar\"] [aria-current=\"page\"] {\n"
        f"        background: rgba({acc_r}, {acc_g}, {acc_b}, 0.12) !important;  /* ← FUNDO ITEM ATIVO SIDEBAR */\n"
        f"        border-left: 3px solid {accent} !important;       /* ← BORDA ITEM ATIVO SIDEBAR */\n"
        "        border-radius: 0 8px 8px 0 !important;\n"
        "    }\n\n"
        "    /* 3D. Hover dos itens na Sidebar */\n"
        "    [data-testid=\"stSidebar\"] a:hover {\n"
        "        background: rgba(255, 255, 255, 0.05) !important;  /* ← HOVER SIDEBAR ITEMS */\n"
        "        border-radius: 8px !important;\n"
        "    }\n\n"
        "    /* 3E. Títulos dentro da Sidebar */\n"
        "    [data-testid=\"stSidebar\"] h1,\n"
        "    [data-testid=\"stSidebar\"] h2,\n"
        "    [data-testid=\"stSidebar\"] h3 {\n"
        f"        color: {text1} !important;    /* ← TÍTULOS SIDEBAR */\n"
        "    }\n\n"
        "    /* 3F. Inputs/Selectbox dentro da Sidebar */\n"
        "    [data-testid=\"stSidebar\"] input,\n"
        "    [data-testid=\"stSidebar\"] [data-testid=\"stSelectbox\"] > div > div {\n"
        "        background: rgba(255, 255, 255, 0.06) !important;  /* ← FUNDO INPUTS SIDEBAR */\n"
        "        color: #e2e8f0 !important;\n"
        "        border-color: rgba(255, 255, 255, 0.1) !important;\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       4. CARDS DE MÉTRICAS E CONTAINERS\n"
        "       ═══════════════════════════════════════ */\n"
        "    div[data-testid=\"stMetric\"] {\n"
        f"        background: linear-gradient(145deg, rgba({crd_r},{crd_g},{crd_b},{opacity_card:.2f}), rgba({bg1_r},{bg1_g},{bg1_b},{opacity_card:.2f})); /* ← FUNDO CARD */\n"
        "        border: 1px solid rgba(255, 255, 255, 0.07);\n"
        "        padding: 20px;\n"
        f"        border-radius: {r_card}px;\n"
        "        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.15);\n"
        "        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);\n"
        "    }\n"
        "    div[data-testid=\"stMetric\"]:hover {\n"
        "        transform: translateY(-4px);\n"
        f"        border-color: {accent};        /* ← COR HOVER BORDA CARD MÉTRICA */\n"
        "        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3);\n"
        "    }\n\n"
        "    [data-testid=\"stVerticalBlock\"] > div > div > div[data-testid=\"stContainer\"] {\n"
        f"        background: rgba({crd_r},{crd_g},{crd_b},{opacity_card:.2f});  /* ← FUNDO CONTAINER */\n"
        f"        backdrop-filter: blur({blur_cd}px);\n"
        "        border: 1px solid rgba(255, 255, 255, 0.08);\n"
        f"        border-radius: {r_card}px;\n"
        "        padding: 24px;\n"
        "        transition: border 0.3s ease;\n"
        "    }\n"
        "    [data-testid=\"stVerticalBlock\"] > div > div > div[data-testid=\"stContainer\"]:hover {\n"
        f"        border-color: rgba({acc_r}, {acc_g}, {acc_b}, 0.4);  /* ← HOVER BORDA CONTAINER */\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       5. BOTÕES\n"
        "       ═══════════════════════════════════════ */\n"
        "    .stButton > button {\n"
        f"        border-radius: {r_btn}px !important;\n"
        "        font-weight: 600 !important;\n"
        "        letter-spacing: 0.5px !important;\n"
        "        transition: all 0.2s ease !important;\n"
        "        border: 1px solid rgba(255,255,255,0.1) !important;\n"
        f"        background: linear-gradient(to bottom right, {accent}, {accent2}) !important;  /* ← COR BOTÃO */\n"
        "        color: white !important;      /* ← TEXTO BOTÃO */\n"
        "    }\n"
        "    .stButton > button:hover {\n"
        "        transform: scale(1.02) !important;\n"
        f"        box-shadow: 0 0 15px rgba({acc_r}, {acc_g}, {acc_b}, 0.4) !important;  /* ← GLOW HOVER BOTÃO */\n"
        "    }\n"
        "    .stButton > button[kind=\"secondary\"] {\n"
        "        background: rgba(255,255,255,0.06) !important;   /* ← BOTÃO SECUNDÁRIO */\n"
        f"        color: {text2} !important;\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       6. INPUTS E SELECTBOX (Conteúdo principal)\n"
        "       ═══════════════════════════════════════ */\n"
        "    .stTextInput > div > div > input,\n"
        "    .stSelectbox > div > div > div,\n"
        "    .stTextarea textarea {\n"
        f"        border-radius: {r_inp}px !important;\n"
        f"        background-color: rgba({bg1_r},{bg1_g},{bg1_b},0.6) !important;    /* ← FUNDO INPUT */\n"
        "        border: 1px solid rgba(255,255,255,0.1) !important;\n"
        f"        color: {text1} !important;   /* ← TEXTO INPUT */\n"
        "    }\n"
        "    .stTextInput > div > div > input:focus,\n"
        "    .stTextarea textarea:focus {\n"
        f"        border-color: {accent} !important;  /* ← BORDA FOCUS INPUT */\n"
        f"        box-shadow: 0 0 0 2px rgba({acc_r},{acc_g},{acc_b},0.15) !important;\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       7. HEADER / TOPO\n"
        "       ═══════════════════════════════════════ */\n"
        "    header[data-testid=\"stHeader\"] { background: transparent !important; }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       8. SCROLLBARS\n"
        "       ═══════════════════════════════════════ */\n"
        "    ::-webkit-scrollbar { width: 6px; }\n"
        f"    ::-webkit-scrollbar-track {{ background: {bg2}; }}          /* ← TRACK SCROLLBAR */\n"
        f"    ::-webkit-scrollbar-thumb {{ background: {card_bg}; border-radius: 100px; }}  /* ← THUMB SCROLLBAR */\n"
        f"    ::-webkit-scrollbar-thumb:hover {{ background: {accent}; }}   /* ← HOVER SCROLLBAR */\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       9. TABS\n"
        "       ═══════════════════════════════════════ */\n"
        "    button[data-baseweb=\"tab\"] {\n"
        "        background-color: transparent !important;\n"
        "        font-weight: 600 !important;\n"
        "        border-bottom-width: 2px !important;\n"
        "        color: #94a3b8 !important;    /* ← COR TAB INATIVA */\n"
        "    }\n"
        "    button[data-baseweb=\"tab\"][aria-selected=\"true\"] {\n"
        "        color: #ffffff !important;    /* ← COR TAB ATIVA */\n"
        "    }\n"
        "    div[data-baseweb=\"tab-highlight\"] {\n"
        f"        background-color: {accent} !important;  /* ← SUBLINHADO TAB ATIVA */\n"
        "    }\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       10. TIPOGRAFIA GERAL (Conteúdo principal)\n"
        "       ═══════════════════════════════════════ */\n"
        f"    p, .stMarkdown p {{ color: {text2}; }}          /* ← TEXTO SECUNDÁRIO */\n"
        f"    label {{ color: {text2} !important; }}           /* ← LABELS */\n"
        f"    h1, h2, h3 {{ color: {text1} !important; }}     /* ← TÍTULOS */\n\n"
        "    /* ═══════════════════════════════════════\n"
        "       11. OCULTAR ELEMENTOS STREAMLIT\n"
        "       ═══════════════════════════════════════ */\n"
        "    #MainMenu { visibility: hidden; }\n"
        "    footer { visibility: hidden; }\n"
        "    .stAppDeployButton, .stDeployButton { display: none !important; }\n"
        "    </style>\n"
    )

    return (
        'import streamlit as st\n\n'
        '# ══════════════════════════════════════════════════════════════════\n'
        '# CSS ESTÁTICO — edite chaves simples { } livremente — sem f-string\n'
        '# ══════════════════════════════════════════════════════════════════\n'
        '_CSS_STATIC = """\n'
        + css +
        '"""\n\n'
        'def apply_modern_style(logo_url=""):\n'
        '    """\n'
        f'    Tema gerado pelo Editor Visual em {datetime.now().strftime("%d/%m/%Y %H:%M")}\n'
        '    Edite _CSS_STATIC acima — chaves simples funcionam normalmente.\n'
        '    """\n'
        '    st.markdown(_CSS_STATIC, unsafe_allow_html=True)\n'
        '    if logo_url:\n'
        '        st.markdown(f"""\n'
        '        <style>\n'
        '        header[data-testid="stHeader"]::after {{\n'
        '            content: ""; position: absolute; left: 50%; top: 50%;\n'
        '            transform: translate(-50%, -50%); width: 220px; height: 60px;\n'
        '            background-image: url("{logo_url}"); background-size: contain;\n'
        '            background-repeat: no-repeat; background-position: center; z-index: 1000;\n'
        '        }}\n'
        '        </style>\n'
        '        """, unsafe_allow_html=True)\n\n\n'
        + _TAIL_FUNCTIONS
    )


# ─── PRESETS EMBUTIDOS ──────────────────────────────────────────────────────────
PRESETS = {
    "🌌 Dark Navy (Padrão)": {
        "bg1":"#0f172a","bg2":"#020617","accent":"#0ea5e9","accent2":"#0284c7",
        "text1":"#f1f5f9","text2":"#94a3b8","card_bg":"#1e293b","sidebar":"#0f172a",
        "font":"Outfit","r_card":16,"r_btn":12,"r_inp":10,"blur_sb":15,"blur_cd":10,"opacity_card":0.7
    },
    "🟢 Matrix Verde": {
        "bg1":"#000000","bg2":"#000000","accent":"#1fff00","accent2":"#16d900",
        "text1":"#1fff00","text2":"#22ff10","card_bg":"#0a1a0a","sidebar":"#000000",
        "font":"Space Grotesk","r_card":8,"r_btn":6,"r_inp":6,"blur_sb":8,"blur_cd":6,"opacity_card":0.8
    },
    "🌊 Ocean Blue": {
        "bg1":"#0c1a2e","bg2":"#060f1e","accent":"#38bdf8","accent2":"#0284c7",
        "text1":"#e0f2fe","text2":"#7dd3fc","card_bg":"#0f2847","sidebar":"#091628",
        "font":"Inter","r_card":18,"r_btn":14,"r_inp":12,"blur_sb":20,"blur_cd":12,"opacity_card":0.6
    },
    "🟣 Cyberpunk Roxo": {
        "bg1":"#0d001a","bg2":"#070010","accent":"#c026d3","accent2":"#9333ea",
        "text1":"#fdf4ff","text2":"#e879f9","card_bg":"#1a0033","sidebar":"#0d001a",
        "font":"Space Grotesk","r_card":4,"r_btn":4,"r_inp":4,"blur_sb":10,"blur_cd":8,"opacity_card":0.75
    },
    "🔴 Crimson Dark": {
        "bg1":"#1a0000","bg2":"#0d0000","accent":"#ef4444","accent2":"#b91c1c",
        "text1":"#fef2f2","text2":"#fca5a5","card_bg":"#2d0000","sidebar":"#1a0000",
        "font":"Outfit","r_card":14,"r_btn":10,"r_inp":8,"blur_sb":12,"blur_cd":8,"opacity_card":0.7
    },
    "🌙 Midnight Gray": {
        "bg1":"#111111","bg2":"#0a0a0a","accent":"#a3a3a3","accent2":"#737373",
        "text1":"#f5f5f5","text2":"#a3a3a3","card_bg":"#222222","sidebar":"#111111",
        "font":"DM Sans","r_card":20,"r_btn":16,"r_inp":12,"blur_sb":20,"blur_cd":14,"opacity_card":0.65
    },
    "☀️ Light Mode": {
        "bg1":"#f8fafc","bg2":"#e2e8f0","accent":"#0284c7","accent2":"#0369a1",
        "text1":"#0f172a","text2":"#475569","card_bg":"#ffffff","sidebar":"#f1f5f9",
        "font":"Poppins","r_card":16,"r_btn":12,"r_inp":10,"blur_sb":0,"blur_cd":0,"opacity_card":0.95
    },
    "🟠 Sunset Orange": {
        "bg1":"#1c0a00","bg2":"#0f0500","accent":"#f97316","accent2":"#ea580c",
        "text1":"#fff7ed","text2":"#fdba74","card_bg":"#2d1200","sidebar":"#1c0a00",
        "font":"Nunito","r_card":20,"r_btn":16,"r_inp":12,"blur_sb":15,"blur_cd":10,"opacity_card":0.7
    },
}

# ─── STATE: carregar config atual ──────────────────────────────────────────────
if "cfg" not in st.session_state:
    try:
        content = load_tema()
        # Filtra hex codes que parecem ser do tema principal, não do bloco de licença
        hex_list = re.findall(r'#([0-9a-fA-F]{6})', content.split('def apply_license_style')[0])
        if not hex_list: hex_list = re.findall(r'#([0-9a-fA-F]{6})', content)
        
        font_match = re.search(r"family=([A-Za-z+]+):wght", content)
        font_current = font_match.group(1).replace('+', ' ') if font_match else "Outfit"
        
        st.session_state.cfg = {
            "bg1": f"#{hex_list[0]}" if len(hex_list) > 0 else "#0f172a",
            "bg2": f"#{hex_list[1]}" if len(hex_list) > 1 else "#020617",
            "accent": f"#{hex_list[2]}" if len(hex_list) > 2 else "#0ea5e9",
            "accent2": f"#{hex_list[3]}" if len(hex_list) > 3 else "#0284c7",
            "text1": "#f1f5f9", "text2": "#94a3b8",
            "card_bg": "#1e293b", "sidebar": "#0f172a",
            "font": font_current, "r_card": 16, "r_btn": 12, "r_inp": 10,
            "blur_sb": 15, "blur_cd": 10, "opacity_card": 0.7
        }
    except Exception as e:
        st.session_state.cfg = PRESETS["🌌 Dark Navy (Padrão)"].copy()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎨 Editor de Tema")
    st.caption("JUVIKS07 — Visual Designer")
    st.divider()

    st.markdown('<div class="section-hdr">Salvar Meu Preset</div>', unsafe_allow_html=True)
    with st.expander("➕ Salvar Configurações como Novo Preset", expanded=False):
        novo_nome = st.text_input("Nome:", placeholder="Ex: Tema Azulado")
        if st.button("💾 Salvar Preset", use_container_width=True):
            if novo_nome.strip():
                nome_arq = f"{novo_nome.strip().replace(' ', '_').lower()}.json"
                with open(os.path.join(PRESET_DIR, nome_arq), 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.cfg, f, indent=2)
                st.success(f"Preset '{novo_nome}' salvo!")
                st.rerun()
            else:
                st.error("Digite um nome!")

    custom_presets = [f for f in os.listdir(PRESET_DIR) if f.endswith(".json")]
    if custom_presets:
        st.markdown('<div class="section-hdr">📂 Meus Presets Salvos</div>', unsafe_allow_html=True)
        for cp in custom_presets:
            pn = cp.replace(".json", "").replace("_", " ").title()
            cols1, cols2 = st.columns([5, 1])
            if cols1.button(f"⭐ {pn}", key=f"cust_{cp}", use_container_width=True):
                with open(os.path.join(PRESET_DIR, cp), 'r', encoding='utf-8') as f:
                    st.session_state.cfg = json.load(f)
                save_tema(gen_theme(st.session_state.cfg), f"meupreset_{pn.replace(' ', '')}")
                st.rerun()
            if cols2.button("🗑️", key=f"del_{cp}", help="Apagar", use_container_width=True):
                os.remove(os.path.join(PRESET_DIR, cp))
                st.rerun()
        st.divider()

    st.markdown('<div class="section-hdr">Presets Prontos</div>', unsafe_allow_html=True)
    for nome, preset in PRESETS.items():
        if st.button(nome, key=f"preset_{nome}", use_container_width=True):
            st.session_state.cfg = preset.copy()
            save_tema(gen_theme(st.session_state.cfg), f"preset_{nome.split()[0]}")
            st.rerun()

    st.divider()
    st.markdown('<div class="section-hdr">Importar / Exportar</div>', unsafe_allow_html=True)

    cfg_json = json.dumps(st.session_state.cfg, indent=2)
    st.download_button("⬇️ Exportar Tema (JSON)", cfg_json,
                       file_name=f"tema_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                       mime="application/json", use_container_width=True)

    uploaded = st.file_uploader("⬆️ Importar Tema (JSON)", type="json")
    if uploaded:
        try:
            imported = json.load(uploaded)
            st.session_state.cfg = imported
            save_tema(gen_theme(imported), "importado")
            st.success("✅ Tema importado!")
            st.rerun()
        except:
            st.error("JSON inválido.")

# ─── TABS PRINCIPAIS ────────────────────────────────────────────────────────────
tab_cores, tab_layout, tab_tip, tab_prev, tab_code, tab_bkp = st.tabs([
    "🎨 Cores", "📐 Layout & Efeitos", "🔤 Tipografia",
    "👁️ Preview Completo", "📝 Código Direto", "💾 Backups"
])
cfg = st.session_state.cfg

# ══════════════════════════════════════════════════════
# TAB 1 — CORES
# ══════════════════════════════════════════════════════
with tab_cores:
    st.subheader("🎨 Paleta de Cores")
    st.caption("Todas as cores do sistema em um só lugar.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-hdr">🌑 Fundo</div>', unsafe_allow_html=True)
        cfg['bg1'] = st.color_picker("Fundo Principal (centro do gradiente)", cfg['bg1'], key="cp_bg1")
        cfg['bg2'] = st.color_picker("Fundo Externo (borda do gradiente)", cfg['bg2'], key="cp_bg2")

        st.markdown('<div class="section-hdr">💎 Acento & CTA</div>', unsafe_allow_html=True)
        cfg['accent']  = st.color_picker("Cor de Destaque Principal (botões, links, ícones)", cfg['accent'], key="cp_acc")
        cfg['accent2'] = st.color_picker("Cor de Destaque Secundária (gradiente do botão, hover)", cfg['accent2'], key="cp_acc2")

        st.markdown('<div class="section-hdr">📝 Sidebar</div>', unsafe_allow_html=True)
        cfg['sidebar'] = st.color_picker("Cor da Sidebar", cfg['sidebar'], key="cp_sb")

    with c2:
        st.markdown('<div class="section-hdr">🗂️ Cards & Containers</div>', unsafe_allow_html=True)
        cfg['card_bg'] = st.color_picker("Fundo dos Cards", cfg['card_bg'], key="cp_card")

        st.markdown('<div class="section-hdr">✏️ Texto</div>', unsafe_allow_html=True)
        cfg['text1']   = st.color_picker("Texto Principal (títulos, valores)", cfg['text1'], key="cp_t1")
        cfg['text2']   = st.color_picker("Texto Secundário (labels, subtítulos)", cfg['text2'], key="cp_t2")

        # Paleta resumida
        st.markdown('<div class="section-hdr">🖼️ Paleta Atual</div>', unsafe_allow_html=True)
        palette_html = "".join([
            f'<span style="display:inline-block;width:36px;height:36px;border-radius:8px;background:{c};border:2px solid rgba(255,255,255,0.15);margin:3px;title:{c}" title="{c}"></span>'
            for c in [cfg['bg1'], cfg['bg2'], cfg['accent'], cfg['accent2'],
                      cfg['text1'], cfg['text2'], cfg['card_bg'], cfg['sidebar']]
        ])
        st.markdown(f"<div style='margin-top:8px'>{palette_html}</div>", unsafe_allow_html=True)

    if st.button("💾 Salvar Cores", type="primary", use_container_width=True):
        save_tema(gen_theme(cfg), "cores")
        st.success("✅ Cores salvas!")

# ══════════════════════════════════════════════════════
# TAB 2 — LAYOUT & EFEITOS
# ══════════════════════════════════════════════════════
with tab_layout:
    st.subheader("📐 Layout, Bordas e Efeitos")
    la, lb = st.columns(2)

    with la:
        st.markdown('<div class="section-hdr">📐 Raios de Borda (px)</div>', unsafe_allow_html=True)
        cfg['r_card'] = st.slider("Cards e Containers",  2, 40, cfg.get('r_card', 16))
        cfg['r_btn']  = st.slider("Botões",              2, 30, cfg.get('r_btn', 12))
        cfg['r_inp']  = st.slider("Inputs e Selects",    2, 24, cfg.get('r_inp', 10))

        st.markdown('<div class="section-hdr">💨 Efeito Glassmorphism</div>', unsafe_allow_html=True)
        cfg['blur_sb'] = st.slider("Blur da Sidebar (px)", 0, 40, cfg.get('blur_sb', 15))
        cfg['blur_cd'] = st.slider("Blur dos Cards (px)",  0, 30, cfg.get('blur_cd', 10))
        cfg['opacity_card'] = st.slider("Opacidade dos Cards", 0.1, 1.0, float(cfg.get('opacity_card', 0.7)), step=0.05)

    with lb:
        st.markdown("#### Preview dos Efeitos")
        r = cfg['r_card']
        bl = cfg['blur_cd']
        op = cfg['opacity_card']
        acc = cfg['accent']
        bg1 = cfg['bg1']
        t1  = cfg['text1']
        t2  = cfg['text2']
        cbg = cfg['card_bg']
        cbg_rgb = ', '.join(str(x) for x in hex_to_rgb(cbg))
        bg1_rgb = ', '.join(str(x) for x in hex_to_rgb(bg1))

        st.markdown(f"""
        <div style="background:radial-gradient(circle,{bg1},{cfg['bg2']});border-radius:16px;padding:20px">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
                <div style="background:rgba({cbg_rgb},{op});backdrop-filter:blur({bl}px);
                            border-radius:{r}px;border:1px solid rgba(255,255,255,0.08);padding:16px">
                    <div style="color:{t2};font-size:.75rem;margin-bottom:4px">Faturamento</div>
                    <div style="color:{acc};font-size:1.4rem;font-weight:700">R$ 24.500</div>
                </div>
                <div style="background:rgba({cbg_rgb},{op});backdrop-filter:blur({bl}px);
                            border-radius:{r}px;border:1px solid rgba(255,255,255,0.08);padding:16px">
                    <div style="color:{t2};font-size:.75rem;margin-bottom:4px">Lucro</div>
                    <div style="color:#22c55e;font-size:1.4rem;font-weight:700">R$ 9.800</div>
                </div>
            </div>
            <div style="background:linear-gradient(135deg,{acc},{cfg['accent2']});
                        text-align:center;padding:10px;border-radius:{cfg['r_btn']}px;
                        color:white;font-weight:600;font-size:.9rem">
                Botão Principal — raio {cfg['r_btn']}px
            </div>
            <div style="margin-top:10px;background:rgba({bg1_rgb},0.6);
                        border:1px solid rgba(255,255,255,0.1);
                        border-radius:{cfg['r_inp']}px;padding:10px 14px;color:{t2};font-size:.82rem">
                Campo de Texto — raio {cfg['r_inp']}px
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("💾 Salvar Layout", type="primary", use_container_width=True):
        save_tema(gen_theme(cfg), "layout")
        st.success("✅ Layout salvo!")

# ══════════════════════════════════════════════════════
# TAB 3 — TIPOGRAFIA
# ══════════════════════════════════════════════════════
with tab_tip:
    st.subheader("🔤 Tipografia e Fonte")
    fonts = ["Outfit","Space Grotesk","Inter","Roboto","Poppins","Nunito",
             "DM Sans","Montserrat","Raleway","Barlow","Exo 2","Syne","Manrope"]

    idx_f = fonts.index(cfg.get('font', 'Space Grotesk')) if cfg.get('font') in fonts else 0
    cfg['font'] = st.selectbox("Fonte do Sistema", fonts, index=idx_f)

    font_url = cfg['font'].replace(' ', '+')
    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family={font_url}:wght@300;400;600;700&display=swap" rel="stylesheet">
    <div style="background:rgba(30,41,59,0.4);border-radius:16px;padding:28px;border:1px solid rgba(255,255,255,0.08);font-family:'{cfg['font']}',sans-serif">
        <div style="font-size:2rem;font-weight:700;color:{cfg['accent']};margin-bottom:8px">
            {cfg['font']}
        </div>
        <div style="font-size:1.1rem;color:{cfg['text1']};margin-bottom:6px;font-weight:600">
            Texto Principal — 600 weight
        </div>
        <div style="font-size:.95rem;color:{cfg['text2']};margin-bottom:6px">
            Texto Secundário — 400 weight — Lorem ipsum dolor sit amet consectetur
        </div>
        <div style="font-size:.8rem;color:{cfg['text2']};opacity:.7">
            Caption e Labels — 300 weight — R$ 18.500,00 | 42 pedidos | 87% conversão
        </div>
        <div style="margin-top:16px;display:flex;gap:10px">
            <div style="background:linear-gradient(135deg,{cfg['accent']},{cfg['accent2']});color:white;padding:8px 18px;border-radius:{cfg['r_btn']}px;font-weight:600;font-size:.85rem">Botão Primário</div>
            <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);color:{cfg['text1']};padding:8px 18px;border-radius:{cfg['r_btn']}px;font-size:.85rem">Botão Secundário</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("💾 Salvar Fonte", type="primary", use_container_width=True):
        save_tema(gen_theme(cfg), "fonte")
        st.success(f"✅ Fonte '{cfg['font']}' salva!")

# ══════════════════════════════════════════════════════
# TAB 4 — PREVIEW COMPLETO
# ══════════════════════════════════════════════════════
with tab_prev:
    st.subheader("👁️ Preview Completo do Sistema")
    acc_rgb  = ', '.join(str(x) for x in hex_to_rgb(cfg['accent']))
    cbg_rgb  = ', '.join(str(x) for x in hex_to_rgb(cfg['card_bg']))
    sbg_rgb  = ', '.join(str(x) for x in hex_to_rgb(cfg['sidebar']))

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family={cfg['font'].replace(' ', '+')}:wght@300;400;600;700&display=swap" rel="stylesheet">
    <div style="background:radial-gradient(circle at 40% 20%,{cfg['bg1']},{cfg['bg2']});
                border-radius:20px;padding:0;overflow:hidden;
                border:1px solid rgba(255,255,255,0.06);font-family:'{cfg['font']}',sans-serif;
                min-height:600px;display:flex">

        <!-- SIDEBAR -->
        <div style="width:200px;background:rgba({sbg_rgb},0.95);
                    backdrop-filter:blur({cfg['blur_sb']}px);
                    border-right:1px solid rgba(255,255,255,0.06);padding:20px 12px;">
            <div style="text-align:center;margin-bottom:24px">
                <div style="background:linear-gradient(135deg,{cfg['accent']},{cfg['accent2']});
                            color:white;padding:6px 14px;border-radius:8px;font-size:.8rem;font-weight:700">
                    JUVIKS07
                </div>
            </div>
            <div style="font-size:.65rem;text-transform:uppercase;letter-spacing:2px;color:{cfg['text2']};margin-bottom:8px">Menu</div>
            {"".join([f'<div style="padding:9px 12px;border-radius:{cfg["r_btn"]}px;margin-bottom:4px;font-size:.82rem;' +
                (f'background:{cfg["accent"]}22;color:{cfg["accent"]};font-weight:600' if i==0 else f'color:{cfg["text2"]}') +
                f'">{emoji} {name}</div>'
                for i,(emoji,name) in enumerate([("🏠","Início"),("👥","Clientes"),("📝","Orçamentos"),
                                                  ("📅","Agenda"),("📊","Dashboard"),("💰","Financeiro"),("✍️","Assinaturas")])])}
        </div>

        <!-- CONTEÚDO -->
        <div style="flex:1;padding:24px">
            <div style="font-size:1.5rem;font-weight:700;color:{cfg['text1']};margin-bottom:4px">Dashboard de Performance</div>
            <div style="font-size:.82rem;color:{cfg['text2']};margin-bottom:20px">Visão geral em tempo real</div>

            <!-- MÉTRICAS -->
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px">
                {"".join([f'''<div style="background:linear-gradient(145deg,rgba({cbg_rgb},{cfg['opacity_card']}),rgba({', '.join(str(x) for x in hex_to_rgb(cfg['bg1']))},{cfg['opacity_card']}));
                               backdrop-filter:blur({cfg['blur_cd']}px);
                               border:1px solid rgba(255,255,255,0.06);border-radius:{cfg['r_card']}px;padding:16px">
                    <div style="font-size:.7rem;color:{cfg['text2']};text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">{label}</div>
                    <div style="font-size:1.3rem;font-weight:700;color:{color}">{value}</div>
                    <div style="font-size:.7rem;color:#22c55e;margin-top:2px">{delta}</div>
                </div>'''
                for label,color,value,delta in [
                    ("Faturamento",cfg['accent'],"R$ 142.500","+12% vs mês ant."),
                    ("Lucro Líquido","#22c55e","R$ 58.200","Margem 41%"),
                    ("Ticket Médio","#fbbf24","R$ 3.840","87 pedidos"),
                    ("Taxa Conversão","#a78bfa","78.4%","+3.2 pontos"),
                ]])}
            </div>

            <!-- TABELA SIMULADA -->
            <div style="background:rgba({cbg_rgb},0.4);backdrop-filter:blur({cfg['blur_cd']}px);
                        border-radius:{cfg['r_card']}px;border:1px solid rgba(255,255,255,0.06);overflow:hidden">
                <div style="padding:14px 18px;border-bottom:1px solid rgba(255,255,255,0.05);
                            font-weight:600;color:{cfg['text1']};font-size:.9rem">Últimos Pedidos</div>
                {"".join([f'''<div style="display:flex;justify-content:space-between;
                              padding:10px 18px;border-bottom:1px solid rgba(255,255,255,0.04);
                              font-size:.82rem;color:{cfg['text2']}">
                    <span style="color:{cfg['text1']}">{client}</span>
                    <span>R$ {value}</span>
                    <span style="color:{sc};background:{sc}22;padding:3px 10px;border-radius:20px;font-size:.7rem;font-weight:700">{status}</span>
                </div>'''
                for client,value,sc,status in [
                    ("João Pereira","8.400","#22c55e","Aprovado"),
                    ("Maria Silva","5.250","#fbbf24","Pendente"),
                    ("Carlos Lima","12.800","#22c55e","Aprovado"),
                    ("Ana Santos","3.100","#ef4444","Cancelado"),
                ]])}
            </div>

            <!-- BOTÕES -->
            <div style="display:flex;gap:10px;margin-top:20px">
                <div style="background:linear-gradient(135deg,{cfg['accent']},{cfg['accent2']});
                            color:white;padding:10px 20px;border-radius:{cfg['r_btn']}px;font-weight:600;font-size:.85rem">
                    ✅ Botão Primário
                </div>
                <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
                            color:{cfg['text1']};padding:10px 20px;border-radius:{cfg['r_btn']}px;font-size:.85rem">
                    Botão Secundário
                </div>
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                            color:{cfg['text2']};padding:10px 16px;border-radius:{cfg['r_inp']}px;font-size:.82rem;min-width:180px">
                    🔍 Campo de busca...
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ SALVAR ESTE TEMA NO SISTEMA", type="primary", use_container_width=True):
        save_tema(gen_theme(cfg), "preview")
        st.session_state.cfg = cfg
        st.success("🎉 Tema aplicado ao sistema com sucesso! Reinicie o JUVIKS07 para ver as mudanças.")
        st.balloons()

# ══════════════════════════════════════════════════════
# TAB 5 — EDITOR DE CÓDIGO DIRETO
# ══════════════════════════════════════════════════════
with tab_code:
    st.subheader("📝 Editor de Código — moderno.py")
    st.caption(f"Edição direta. Backup automático antes de salvar. Arquivo: `{TEMA_FILE}`")
    
    try:
        current_code = load_tema()
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        current_code = ""

    edited = st.text_area("", value=current_code, height=550, label_visibility="collapsed", key="code_editor")

    cc1, cc2, cc3 = st.columns([3, 1, 1])
    with cc1:
        if st.button("💾 Salvar Código", type="primary", use_container_width=True):
            if edited.strip():
                save_tema(edited, "codigo")
                st.success("✅ Código salvo! Backup criado.")
                st.rerun()
            else:
                st.error("Conteúdo vazio. Não salvo.")
    with cc2:
        st.download_button("⬇️ Baixar", edited, "moderno.py", "text/plain", use_container_width=True)
    with cc3:
        if st.button("🔄 Recarregar", use_container_width=True):
            st.rerun()

# ══════════════════════════════════════════════════════
# TAB 6 — BACKUPS
# ══════════════════════════════════════════════════════
with tab_bkp:
    st.subheader("💾 Gerenciador de Backups")
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".py")], reverse=True)

    if not backups:
        st.info("Nenhum backup criado ainda.")
    else:
        st.caption(f"📁 `{BACKUP_DIR}` — **{len(backups)}** backup(s)")

        bk_filter = st.text_input("🔍 Filtrar backups:", placeholder="Ex: cores, layout, 20260308...")
        filtered_bk = [b for b in backups if bk_filter.lower() in b.lower()] if bk_filter else backups

        for i, bk in enumerate(filtered_bk[:20]):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
                c1.markdown(f"📄 `{bk}`")
                try:
                    ts_raw = re.search(r'(\d{8}_\d{6})', bk)
                    if ts_raw:
                        ts = datetime.strptime(ts_raw.group(1), "%Y%m%d_%H%M%S")
                        c2.caption(ts.strftime("🕒 %d/%m/%Y %H:%M:%S"))
                except: pass

                bk_path = os.path.join(BACKUP_DIR, bk)
                with open(bk_path, 'r', encoding='utf-8', errors='replace') as f:
                    bk_content = f.read()

                c3.download_button("⬇️", bk_content, bk, "text/plain",
                                   key=f"dl_{i}", use_container_width=True)

                if c4.button("🔄", key=f"rest_{i}", use_container_width=True, help="Restaurar"):
                    save_tema(bk_content, "restaurado")
                    st.success(f"✅ Restaurado para `{bk}`!")
                    st.rerun()

        st.divider()
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            if len(backups) > 10:
                if st.button(f"🗑️ Limpar antigos (manter 10 mais recentes)", use_container_width=True):
                    for old in backups[10:]:
                        os.remove(os.path.join(BACKUP_DIR, old))
                    st.success("Limpo!")
                    st.rerun()
        with col_del2:
            if st.button("📸 Criar Backup Manual Agora", use_container_width=True, type="primary"):
                save_tema(load_tema(), "manual")
                st.success("✅ Backup manual criado!")
                st.rerun()
