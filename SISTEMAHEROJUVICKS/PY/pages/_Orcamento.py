# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys
import base64

# Define a página atual para o bypass de autenticação
st.session_state["current_page"] = "Orcamento"

# Configuração da página - Deve ser o primeiro comando Streamlit
st.set_page_config(page_title="Orçamento Digital | Juvix", layout="centered", initial_sidebar_state="collapsed")

# Adiciona a raiz do projeto ao sys.path
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import buscar_dados
from utils.documentos import GeradorPDF
import json

def get_logo_base64():
    try:
        df_conf = buscar_dados("SELECT logo_data FROM config LIMIT 1")
        if not df_conf.empty and df_conf.iloc[0]['logo_data']:
            return f"data:image/png;base64,{df_conf.iloc[0]['logo_data']}"
    except: pass
    return None

# Estilo Premium (Fundo escuro, igual ao seu sistema)
sidebar_hide = ""
if not st.session_state.get("autenticado"):
    sidebar_hide = """
    [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {
        display: none !important;
    }
    """

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    .stApp {{
        background: radial-gradient(circle at 50% 50%, #0c1a2e 0%, #060f1e 100%);
        color: #e0f2fe;
    }}
    .main-card {{
        background: rgba(15,40,71,0.60);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }}
    .btn-download {{
        background: linear-gradient(to bottom right, #38bdf8, #0284c7) !important;
        color: white !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        display: inline-block !important;
        margin-top: 15px !important;
    }}
    /* Bloqueio da Barra Lateral apenas para clientes externos */
    {sidebar_hide}
    #MainMenu, footer, header {{ visibility: hidden !important; }}
    </style>
""", unsafe_allow_html=True)

# Capturar ID do orçamento pela URL
params = st.query_params
orc_id = params.get("id")

if not orc_id:
    st.error("❌ Orçamento não especificado ou link inválido.")
    if st.button("🏠 Voltar ao Sistema"):
        st.switch_page("Inicio.py")
    st.stop()

# Buscar dados do orçamento
df_orc = buscar_dados(f"SELECT * FROM orcamentos WHERE id = '{orc_id}'")

if df_orc.empty:
    st.error(f"❌ Orçamento '{orc_id}' não encontrado em nossa base.")
    if st.button("🏠 Voltar ao Sistema"):
        st.switch_page("Inicio.py")
    st.stop()

orc_data = df_orc.iloc[0]

# --- CABEÇALHO ---
logo = get_logo_base64()
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if logo:
        st.image(logo, width=180)
    st.markdown(f"## Orçamento Digital: `{orc_id}`")
    st.markdown(f"Olá, o orçamento solicitado já está disponível para visualização!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- GERAR E EXIBIR PDF ---
with st.spinner("Carregando documento..."):
    try:
        # Buscar dados da empresa e cliente para gerar o PDF na hora
        df_conf = buscar_dados("SELECT * FROM config LIMIT 1")
        emp_d = df_conf.iloc[0].to_dict() if not df_conf.empty else {}
        
        # Buscar cliente
        df_cli = buscar_dados(f"SELECT * FROM clientes WHERE id = '{orc_data['cliente_id']}'")
        cli_row = df_cli.iloc[0]
        cli_d = {"nome": cli_row['nome'], "cnpj": cli_row['cnpj'], "telefone": cli_row['telefone'], "endereco": cli_row['endereco'], "numero": cli_row['numero']}
        
        # Gerar o PDF
        pdf_data = GeradorPDF.criar_pdf(
            id_orc=orc_data['id'], empresa=emp_d, cliente=cli_d, 
            carrinho=json.loads(orc_data['itens_json']), 
            financeiro={"total": orc_data['total'], "forma": orc_data['forma_pagamento'], "data": orc_data['data']}, 
            vendedor=orc_data['vendedor'], validade=orc_data['validade_dias'], estilo='futurista'
        )
        
        if isinstance(pdf_data, str): pdf_data = pdf_data.encode('latin-1', 'replace')
        
        # Botão de Download Manual (Fallback)
        st.download_button("📥 BAIXAR PDF DO ORÇAMENTO", pdf_data, f"Orcamento_{orc_id}.pdf", "application/pdf", use_container_width=True)
        
        # Exibir o PDF no iFrame
        b64 = base64.b64encode(pdf_data).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800" style="border:none;border-radius:12px;background:white;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        st.markdown("<br><p style='text-align:center; color:#64748b; font-size:0.8rem;'>Sistema Juvix &copy; 2026</p>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
