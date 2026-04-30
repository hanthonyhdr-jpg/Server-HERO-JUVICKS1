import streamlit as st
from datetime import datetime as _dt
import requests as _req

def _check_motor() -> bool:
    """Verifica se o motor do WhatsApp está online."""
    try:
        r = _req.get("http://127.0.0.1:3000/status", timeout=2)
        return r.status_code == 200
    except:
        return False

def apply_modern_style(logo_url=None, check_motor: bool = True, nome_empresa: str = "HERO JUVICKS"):
    """Design System Juvicks Elite — Barra superior full-width com status do motor."""

    motor_online = _check_motor() if check_motor else None

    # Badge do motor com animação pulsante
    if motor_online is True:
        motor_badge = (
            "<style>"
            "@keyframes pulse-green {"
            "  0%   { box-shadow: 0 0 0 0 rgba(34,197,94,.6); }"
            "  70%  { box-shadow: 0 0 0 7px rgba(34,197,94,0); }"
            "  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }"
            "}"
            "</style>"
            "<span style='display:inline-flex; align-items:center; gap:6px; "
            "background:rgba(34,197,94,.1); color:#22c55e; "
            "border:1px solid rgba(34,197,94,.3); border-radius:20px; "
            "padding:3px 12px; font-size:.65rem; font-weight:700; letter-spacing:1px;'>"
            "<span style='width:7px; height:7px; border-radius:50%; "
            "background:#22c55e; display:inline-block; "
            "animation: pulse-green 1.5s infinite;'></span>"
            "MOTOR ONLINE</span>"
        )
    elif motor_online is False:
        motor_badge = (
            "<style>"
            "@keyframes pulse-red {"
            "  0%   { box-shadow: 0 0 0 0 rgba(239,68,68,.6); }"
            "  70%  { box-shadow: 0 0 0 7px rgba(239,68,68,0); }"
            "  100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }"
            "}"
            "</style>"
            "<span style='display:inline-flex; align-items:center; gap:6px; "
            "background:rgba(239,68,68,.1); color:#ef4444; "
            "border:1px solid rgba(239,68,68,.3); border-radius:20px; "
            "padding:3px 12px; font-size:.65rem; font-weight:700; letter-spacing:1px;'>"
            "<span style='width:7px; height:7px; border-radius:50%; "
            "background:#ef4444; display:inline-block; "
            "animation: pulse-red 1.5s infinite;'></span>"
            "MOTOR OFFLINE</span>"
        )
    else:
        motor_badge = ""

    # Relógio gerado via Python (sem iframe, sem caixa preta)
    _agora    = _dt.now()
    _dias     = ["SEG","TER","QUA","QUI","SEX","SÁB","DOM"]
    _hora_str = _agora.strftime("%H:%M")
    _data_str = f"{_dias[_agora.weekday()]} · {_agora.strftime('%d/%m/%Y')}"

    # Barra superior full-width
    st.markdown(f"""
        <div id="juvix-topbar" style="
            position: fixed;
            top: 0; left: 0;
            width: 100vw;
            height: 48px;
            background: linear-gradient(90deg, #020817 0%, #0c1a3a 50%, #020817 100%);
            border-bottom: 1px solid rgba(56,189,248,.25);
            box-shadow: 0 1px 30px rgba(14,165,233,.12);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 9999999;
            box-sizing: border-box;
        ">
            <div style="display:flex; align-items:center; gap:14px; flex:1; min-width:0;">
                <span style="color:#38bdf8; font-size:.72rem; font-weight:700;
                             letter-spacing:4px; white-space:nowrap;">
                    🛡️&nbsp;&nbsp;{nome_empresa.upper()}&nbsp;&nbsp;·&nbsp;&nbsp;SISTEMA OPERACIONAL
                </span>
                {motor_badge}
            </div>
            <div style="display:flex; align-items:center; flex-shrink:0; 
                        font-family:'JetBrains Mono',monospace;">
                <div id="juvix-clock" style="color:#38bdf8; font-size:1.15rem; font-weight:800;
                            letter-spacing:1px; line-height:1;">{_hora_str}</div>
                <div id="juvix-date" style="color:#64748b; font-size:.7rem; font-weight:500;
                            letter-spacing:.5px; line-height:1; margin-left:12px; 
                            padding-left:12px; border-left:1px solid rgba(255,255,255,0.1);">{_data_str}</div>
            </div>
        </div>
        
        <img src="x" style="display:none;" onerror="
            if (!window.clockInterval) {{
                const updateClock = () => {{
                    const now = new Date();
                    const pad = n => String(n).padStart(2,'0');
                    const days = ['DOM','SEG','TER','QUA','QUI','SEX','SÁB'];
                    const clk = document.getElementById('juvix-clock');
                    const dt  = document.getElementById('juvix-date');
                    if (clk) clk.textContent = pad(now.getHours())+':'+pad(now.getMinutes());
                    if (dt)  dt.textContent  = days[now.getDay()]+' · '+pad(now.getDate())+'/'+pad(now.getMonth()+1)+'/'+now.getFullYear();
                }};
                window.clockInterval = setInterval(updateClock, 1000);
            }}
        ">
    """, unsafe_allow_html=True)

    # CSS global
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

        /* ── RESET PÓS-LOGIN (sobrescreve qualquer CSS da tela de login) ── */
        html, body, .stApp {
            overflow: auto !important;
            visibility: visible !important;
            display: block !important;
        }
        iframe { position: static !important; width: auto !important; height: auto !important; z-index: auto !important; }
        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            display: flex !important;
        }

        /* ── BASE ─────────────────────────────────── */
        html, body, .stApp {
            background: #020817 !important;
            font-family: 'Inter', sans-serif !important;
            color: #e2e8f0 !important;
        }

        /* Esconder header padrão do Streamlit */
        header[data-testid="stHeader"] { display: none !important; }

        /* ── ESPAÇAMENTO (compensar barra fixa) ────── */
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 4rem !important;
            max-width: 1280px !important;
            margin: 0 auto !important;
        }

        /* Mostrar botões de controle da sidebar */
        [data-testid="collapsedControl"] {
            display: block !important;
            margin-top: 50px !important; /* Ajuste para não ficar embaixo da topbar */
            z-index: 999999 !important;
        }

        /* Ocultar link da página 'Orcamento' (pública) no menu lateral sem esconder as de admin */
        [data-testid="stSidebarNav"] ul li a[href$="/Orcamento"] {
            display: none !important;
        }

        /* ── BARRA LATERAL ─────────────────────────── */
        section[data-testid="stSidebar"] {
            background: #060f1e !important;
            border-right: 1px solid rgba(56,189,248,.1) !important;
            margin-top: 48px !important;
            z-index: 100 !important; /* Baixamos bem o z-index da sidebar */
        }
        [data-testid="stSidebarNav"] a {
            border-radius: 8px !important;
            color: #94a3b8 !important;
            font-size: .85rem !important;
            font-weight: 500 !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: rgba(14,165,233,.12) !important;
            color: #38bdf8 !important;
            border-left: 3px solid #38bdf8 !important;
        }

        /* ── CARDS ─────────────────────────────────── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(13,21,45,.7) !important;
            border: 1px solid rgba(255,255,255,.06) !important;
            border-radius: 14px !important;
            padding: 22px 24px !important;
            box-shadow: 0 4px 24px rgba(0,0,0,.25) !important;
            transition: border-color .25s ease, box-shadow .25s ease !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(56,189,248,.25) !important;
            box-shadow: 0 8px 32px rgba(0,0,0,.4) !important;
        }

        /* ── BOTÕES ────────────────────────────────── */
        .stButton > button {
            background: rgba(15,30,60,.6) !important;
            border: 1px solid rgba(56,189,248,.18) !important;
            border-radius: 7px !important;
            color: #94a3b8 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: .78rem !important;
            font-weight: 600 !important;
            padding: 7px 14px !important;
            letter-spacing: .3px !important;
            transition: all .18s ease !important;
            white-space: nowrap !important;
        }
        .stButton > button:hover {
            background: rgba(14,165,233,.12) !important;
            border-color: #38bdf8 !important;
            color: #e0f2fe !important;
            box-shadow: 0 0 12px rgba(56,189,248,.15) !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg,#0ea5e9,#0369a1) !important;
            border: none !important;
            color: #fff !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg,#38bdf8,#0ea5e9) !important;
            box-shadow: 0 0 20px rgba(56,189,248,.35) !important;
        }

        /* ── DOWNLOAD BUTTON ───────────────────────── */
        [data-testid="stDownloadButton"] > button {
            background: rgba(15,30,60,.6) !important;
            border: 1px solid rgba(56,189,248,.18) !important;
            border-radius: 7px !important;
            color: #94a3b8 !important;
            font-size: .78rem !important;
            font-weight: 600 !important;
            padding: 7px 14px !important;
            white-space: nowrap !important;
        }
        [data-testid="stDownloadButton"] > button:hover {
            border-color: #38bdf8 !important;
            color: #e0f2fe !important;
        }

        /* ── INPUTS / SELECTS ──────────────────────── */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        textarea {
            background: rgba(5,10,25,.6) !important;
            border-color: rgba(255,255,255,.08) !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
        }

        /* ── MÉTRICAS (Molduras Premium) ────────────── */
        [data-testid="metric-container"] {
            background: rgba(14,165,233,0.05) !important;
            border: 1px solid rgba(14,165,233,0.2) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3), inset 0 0 10px rgba(14,165,233,0.05) !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="metric-container"]:hover {
            border-color: rgba(56,189,248,0.6) !important;
            background: rgba(14,165,233,0.08) !important;
            box-shadow: 0 0 20px rgba(14,165,233,0.15) !important;
            transform: translateY(-2px);
        }
        [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-size: .7rem !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }

        /* ── DIVISORES ─────────────────────────────── */
        hr { border-color: rgba(255,255,255,.05) !important; }

        /* ── SCROLLBAR ─────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #020817; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 6px; }
        ::-webkit-scrollbar-thumb:hover { background: #334155; }
        </style>
    """, unsafe_allow_html=True)


def get_login_style():
    """CSS para centralização da tela de login."""
    return """
        <style>
        .block-container {
            position: fixed !important;
            top: 50% !important; left: 50% !important;
            transform: translate(-50%, -50%) !important;
            max-width: 420px !important;
            padding: 0 !important;
        }
        [data-testid="stSidebar"] { display: none !important; }
        header { display: none !important; }
        #juvix-topbar { display: none !important; }
        html, body { overflow: hidden !important; background: #020817 !important; }
        </style>
    """
