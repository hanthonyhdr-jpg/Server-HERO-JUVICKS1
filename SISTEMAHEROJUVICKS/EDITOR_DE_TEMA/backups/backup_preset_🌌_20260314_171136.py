import streamlit as st

def apply_modern_style(logo_url=""):
    """
    Injeta CSS Premium para modernizar o sistema JUVIKS07.
    Focado em Dark Mode, Glassmorphism e Micro-animações.
    """
    st.markdown(f"""
        <style>
        /* 1. Cores e Fontes Globais */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');
        
        html, body, [class*="st-"]:not(i):not(span):not([data-testid="stIcon"]) {{
            font-family: 'Space Grotesk', sans-serif;
        }}

        /* Correção para Ícones do Streamlit */
        [data-testid="stIcon"], i, span[data-testid="stIcon"] {{
            font-family: "Material Symbols Outlined", "Material Icons", "Segoe UI Symbol", sans-serif !important;
        }}

        .stApp {{
            background: radial-gradient(circle at 50% 50%, #000000 0%, #000000 100%);
            color: #1fff00;
        }}

        /* Logo no Header */
        header[data-testid="stHeader"]::after {{
            content: ""; position: absolute; left: 50%; top: 50%;
            transform: translate(-50%, -50%); width: 220px; height: 60px;
            background-image: url("{logo_url}"); background-size: contain;
            background-repeat: no-repeat; background-position: center; z-index: 1000;
        }}

        /* 2. Sidebar Premium */
        [data-testid="stSidebar"] {{
            background-color: rgba(15, 23, 42, 0.8) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}

        [data-testid="stSidebarNav"] {{
            padding-top: 2rem;
        }}

        /* 3. Cards de Métricas e Contêineres */
        div[data-testid="stMetric"] {{
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.7));
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-4px);
            border-color: #1fff00;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}

        [data-testid="stVerticalBlock"] > div > div > div[data-testid="stContainer"] {{
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            transition: border 0.3s ease;
        }}
        
        [data-testid="stVerticalBlock"] > div > div > div[data-testid="stContainer"]:hover {{
            border-color: rgba(14, 165, 233, 0.5);
        }}

        /* 4. Botões Estilizados */
        .stButton > button {{
            border-radius: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.2s ease !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background: linear-gradient(to bottom right, #1fff00, #1fff00) !important;
            color: white !important;
        }}

        .stButton > button:hover {{
            transform: scale(1.02) !important;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.4) !important;
        }}
        
        .stButton > button[kind="secondary"] {{
            background: rgba(255, 255, 255, 0.05) !important;
        }}

        /* 5. Inputs e Seletores */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {{
            border-radius: 10px !important;
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}

        /* 6. Cabeçalho Oculto para Design Limpo */
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        
        /* 7. Scrollbars */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #000000;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #000000;
            border-radius: 100px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #334155;
        }}

        /* 8. Tabs Premium */
        button[data-baseweb="tab"] {{
            background-color: transparent !important;
            font-weight: 600 !important;
            border-bottom-width: 2px !important;
        }}
        
        div[data-baseweb="tab-highlight"] {{
            background-color: #1fff00 !important;
        }}

        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppDeployButton, .stDeployButton {{ display: none !important; }}
        </style>
    """, unsafe_allow_html=True)

def apply_signature_management_style():
    """Aplica CSS para a gestão de assinaturas no painel admin."""
    st.markdown("""
        <style>
        .stat-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 28px; }
        .stat-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px;
            padding: 20px 16px; text-align: center;
            transition: all .25s ease;
            backdrop-filter: blur(10px);
        }
        .stat-card:hover { transform: translateY(-3px); border-color: #1fff00; }
        .stat-num { font-size: 2.1rem; font-weight: 800; color: #1fff00; }
        .stat-label { font-size: .75rem; color: #1fff00; margin-top: 4px; font-weight: 600; text-transform: uppercase; }
        
        .doc-card {
            background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 13px; padding: 16px 18px;
            margin-bottom: 12px; transition: border-color .2s;
        }
        .doc-card:hover { border-color: #1fff00; }
        
        .badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 4px 12px; border-radius: 16px;
            font-size: .7rem; font-weight: 700; text-transform: uppercase;
        }
        .badge-pending  { background: rgba(251,191,36,.1);  border: 1px solid #fbbf24; color: #fbbf24; }
        .badge-signed   { background: rgba(59,130,246,.1);  border: 1px solid #3b82f6; color: #3b82f6; }
        .badge-complete { background: rgba(34,197,94,.1);   border: 1px solid #22c55e; color: #22c55e; }
        .badge-rejected { background: rgba(239,68,68,.1);   border: 1px solid #ef4444; color: #ef4444; }
        </style>
    """, unsafe_allow_html=True)

def get_signature_client_style():
    """Retorna o CSS específico para a página pública de assinatura do cliente."""
    return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');
        html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; }
        .stApp { background: radial-gradient(circle at 50% 50%, #000000 0%, #000000 100%); color: #1fff00; }
        header[data-testid="stHeader"] { background: transparent !important; }
        #MainMenu, footer { visibility: hidden; }
        .stAppDeployButton, .stDeployButton { display: none !important; }
        .client-header {
            background: linear-gradient(135deg, #1fff00, #6366f1);
            padding: 32px; border-radius: 16px; text-align: center; margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.3);
        }
        .client-header h1 { color: white !important; font-size: 1.8rem; font-weight: 700; margin: 0; }
        .client-header p  { color: rgba(255,255,255,.9); margin: 8px 0 0; }
        .info-box {
            background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 16px; padding: 16px; backdrop-filter: blur(10px);
        }
        .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: .85rem; }
        .info-row:last-child { border-bottom: none; }
        .info-key { color: #1fff00; font-weight: 600; }
        .info-val { color: #1fff00; }
        .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
        .stTabs [data-baseweb="tab"] { color: #1fff00 !important; }
        .stTabs [aria-selected="true"] { color: #1fff00 !important; border-bottom-color: #1fff00 !important; }
        .stButton > button {
            border-radius: 13px !important;
            background: linear-gradient(135deg, #1fff00, #1fff00) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px !important;
        }
        </style>
    """

def get_login_style():
    """Retorna o CSS específico para a tela de login."""
    return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');
        
        [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden; }

        .stApp {
            background: radial-gradient(circle at 20% 20%, #000000 0%, #000000 100%) !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        .block-container { padding-top: 0 !important; max-width: 100% !important; }

        .login-card {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }

        .stTextInput label p {
            color: #1fff00 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stTextInput input {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 13px !important;
            color: #f8fafc !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
        }

        .stTextInput input:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.2) !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #1fff00 0%, #1fff00 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 13px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            padding: 14px !important;
            width: 100% !important;
            margin-top: 20px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 20px 25px -5px rgba(14, 165, 233, 0.3) !important;
        }
        
        [data-testid="stCheckbox"] label p { color: #1fff00 !important; }

        [data-testid="stAlert"] {
            border-radius: 13px !important;
            background-color: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        .stAppDeployButton, .stDeployButton { display: none !important; }
        </style>
    """

def apply_license_style():
    """Design 100% IDENTICO ao modelo HTML juviks_activation.html."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
        
        :root {
            --bg: #07080d;
            --surface: #0e1018;
            --border: rgba(255,255,255,0.07);
            --border-glow: rgba(99,197,255,0.3);
            --accent: #63c5ff;
            --accent2: #a78bfa;
            --text: #e8eaf0;
            --muted: #5a5f72;
            --danger: #ff5f6d;
            --success: #4ade80;
            --gold: #f5c842;
        }

        /* Full page styles */
        [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="collapsedControl"], #MainMenu, footer {
            display: none !important;
        }

        .stApp {
            background: var(--bg) !important;
            font-family: 'DM Mono', monospace !important;
            color: var(--text) !important;
            overflow: hidden !important;
        }

        /* Animated noise grain overlay */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 1;
            opacity: 0.35;
        }

        /* Ambient glows */
        .ambient {
            position: fixed;
            border-radius: 50%;
            filter: blur(120px);
            pointer-events: none;
            z-index: 0;
        }
        .ambient-1 {
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(99,197,255,0.07) 0%, transparent 70%);
            top: -100px; left: -100px;
            animation: drift1 12s ease-in-out infinite alternate;
        }
        .ambient-2 {
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(167,139,250,0.06) 0%, transparent 70%);
            bottom: -80px; right: -80px;
            animation: drift2 15s ease-in-out infinite alternate;
        }
        @keyframes drift1 { to { transform: translate(60px, 40px); } }
        @keyframes drift2 { to { transform: translate(-40px, -60px); } }

        /* Block container setup */
        .block-container {
            max-width: 520px !important;
            padding: 0 !important;
            margin: auto !important;
            height: 100vh !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            z-index: 1000;
        }

        /* Card Container */
        .card {
            width: 100%;
            background: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.015) 100%);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 48px 44px;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 0 1px rgba(99,197,255,0.05), 0 40px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06);
            animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) both;
            display: flex;
            flex-direction: column;
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 36px;
        }

        .logo-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(99,197,255,0.08);
            border: 1px solid rgba(99,197,255,0.2);
            border-radius: 6px;
            padding: 5px 12px;
            margin-bottom: 14px;
        }
        .logo-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 8px var(--accent);
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        .logo-badge span {
            font-family: 'Syne', sans-serif;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.15em;
            color: var(--accent);
            text-transform: uppercase;
        }

        .title {
            font-family: 'Syne', sans-serif;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--text);
            line-height: 1.1;
        }
        .title span { color: var(--accent); }

        .status-chip {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,95,109,0.1);
            border: 1px solid rgba(255,95,109,0.25);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 11px;
            font-weight: 500;
            color: var(--danger);
            letter-spacing: 0.05em;
            white-space: nowrap;
        }
        .status-chip::before {
            content: '';
            width: 6px; height: 6px;
            border-radius: 50%;
            background: var(--danger);
            box-shadow: 0 0 6px var(--danger);
            animation: pulse 1.5s ease-in-out infinite;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border), transparent);
            margin-bottom: 32px;
        }

        .info-block {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent);
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 28px;
        }
        .info-label {
            font-size: 10px;
            letter-spacing: 0.12em;
            color: var(--muted);
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .info-value {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'DM Mono', monospace;
            font-size: 15px;
            font-weight: 500;
            color: var(--text);
        }

        .copy-btn {
            background: none;
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--muted);
            cursor: pointer;
            padding: 4px 10px;
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            transition: all 0.2s;
        }
        .copy-btn:hover {
            border-color: var(--accent);
            color: var(--accent);
            background: rgba(99,197,255,0.06);
        }
        .copy-btn.copied {
            border-color: var(--success);
            color: var(--success);
            background: rgba(74,222,128,0.06);
        }

        .section-label {
            font-size: 10px;
            letter-spacing: 0.12em;
            color: var(--muted);
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .segmented-row {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 12px;
        }
        .stTextInput {
            width: 100% !important;
        }
        .segmented-row .stTextInput div div input {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            padding: 14px 10px !important;
            font-family: 'DM Mono', monospace !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            letter-spacing: 0.15em !important;
            color: var(--text) !important;
            text-align: center !important;
            height: 50px !important;
            transition: all 0.2s !important;
        }
        .segmented-row .stTextInput div div input:focus {
            border-color: var(--border-glow) !important;
            background: rgba(99,197,255,0.04) !important;
            box-shadow: 0 0 0 3px rgba(99,197,255,0.08) !important;
        }

        .seg-sep {
            color: var(--muted);
            font-size: 18px;
            user-select: none;
        }

        .input-hint {
            font-size: 11px;
            color: var(--muted);
            text-align: center;
            margin-bottom: 28px;
            letter-spacing: 0.04em;
        }

        .stButton > button {
            width: 100% !important;
            padding: 17px 24px !important;
            background: linear-gradient(135deg, #63c5ff 0%, #a78bfa 100%) !important;
            border: none !important;
            border-radius: 12px !important;
            font-family: 'Syne', sans-serif !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            color: #07080d !important;
            height: 56px !important;
            box-shadow: 0 0 30px rgba(99,197,255,0.2), 0 8px 24px rgba(0,0,0,0.4) !important;
            transition: transform 0.2s, box-shadow 0.2s !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 10px !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 0 50px rgba(99,197,255,0.3), 0 16px 32px rgba(0,0,0,0.5) !important;
        }

        .footer {
            margin-top: 32px;
            padding-top: 22px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .footer-left {
            font-size: 11px;
            color: var(--muted);
        }
        .footer-left strong {
            color: rgba(255,255,255,0.3);
            font-weight: 500;
        }
        .support-link {
            font-size: 11px;
            color: var(--accent);
            text-decoration: none;
            letter-spacing: 0.05em;
            border-bottom: 1px solid rgba(99,197,255,0.25);
            padding-bottom: 1px;
            transition: border-color 0.2s;
        }
        .support-link:hover { border-color: var(--accent); }
        </style>
    """, unsafe_allow_html=True)
