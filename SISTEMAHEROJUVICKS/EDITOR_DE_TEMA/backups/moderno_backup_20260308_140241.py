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
            border-color: #0ea5e9;
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
            background: linear-gradient(to bottom right, #0ea5e9, #0284c7) !important;
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
            background-color: #0ea5e9 !important;
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
        .stat-card:hover { transform: translateY(-3px); border-color: #0ea5e9; }
        .stat-num { font-size: 2.1rem; font-weight: 800; color: #0ea5e9; }
        .stat-label { font-size: .75rem; color: #94a3b8; margin-top: 4px; font-weight: 600; text-transform: uppercase; }
        
        .doc-card {
            background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 13px; padding: 16px 18px;
            margin-bottom: 12px; transition: border-color .2s;
        }
        .doc-card:hover { border-color: #0ea5e9; }
        
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
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
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
        .info-key { color: #94a3b8; font-weight: 600; }
        .info-val { color: #1fff00; }
        .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; }
        .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
        .stTabs [aria-selected="true"] { color: #0ea5e9 !important; border-bottom-color: #0ea5e9 !important; }
        .stButton > button {
            border-radius: 13px !important;
            background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
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
            color: #94a3b8 !important;
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
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
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
        
        [data-testid="stCheckbox"] label p { color: #94a3b8 !important; }

        [data-testid="stAlert"] {
            border-radius: 13px !important;
            background-color: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        .stAppDeployButton, .stDeployButton { display: none !important; }
        </style>
    """

def apply_license_style():
    """Aplica o CSS para a tela de bloqueio de licença."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap');
        
        [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden; }

        .stApp {
            background-color: #000000 !important;
            background-image: 
                radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(79, 70, 229, 0.15) 0px, transparent 50%) !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        .lock-container {
            max-width: 500px;
            margin: 60px auto;
            padding: 40px;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .lock-icon {
            font-size: 64px;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        h1 {
            color: white !important;
            font-size: 28px !important;
            font-weight: 600 !important;
            margin-bottom: 12px !important;
        }

        p {
            color: #94a3b8 !important;
            font-size: 16px !important;
            margin-bottom: 32px !important;
        }

        .stTextInput input {
            background-color: rgba(2, 6, 23, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 13px !important;
            color: white !important;
            padding: 12px 16px !important;
            text-align: center !important;
            letter-spacing: 2px !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 13px !important;
            padding: 12px 24px !important;
            width: 100% !important;
            font-weight: 600 !important;
            margin-top: 10px !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(14, 165, 233, 0.4);
        }

        .support-link {
            display: inline-block;
            margin-top: 24px;
            color: #38bdf8 !important;
            text-decoration: none !important;
            font-size: 14px;
            font-weight: 500;
        }
        .stAppDeployButton, .stDeployButton { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
