import streamlit as st
import os
import sys

# Adiciona a raiz do projeto ao sys.path
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from database import buscar_dados, executar_comando
from TEMAS.moderno import apply_modern_style

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="GERENCIADOR DE ACESSOS - JUVICKS", 
    layout="wide", 
    page_icon="🛡️"
)

# Estilo personalizado para parecer um sistema de segurança isolado
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .security-header {
        padding: 20px;
        background: linear-gradient(90deg, #1e3a8a 0%, #000000 100%);
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="security-header">
    <h1 style='margin:0; color: white;'>🛡️ PROTEÇÃO TOTAL JUVICKS</h1>
    <p style='margin:0; color: #cbd5e1;'>Painel Externo de Controle de Chaves e Auditoria</p>
</div>
""", unsafe_allow_html=True)

# --- 2. LOGIN DO ADMINISTRADOR SUPREMO ---
if "admin_master" not in st.session_state:
    st.session_state.admin_master = False

if not st.session_state.admin_master:
    col_l, col_c, col_r = st.columns([1, 1, 1])
    with col_c:
        st.subheader("Autenticação de Segurança")
        u = st.text_input("Usuário Master")
        p = st.text_input("Senha Master", type="password")
        if st.button("ENTRAR NO GERENCIADOR"):
            # Verifica na tabela de usuários se é admin
            res = buscar_dados("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (u, p))
            if not res.empty and u == 'admin':
                st.session_state.admin_master = True
                st.rerun()
            else:
                st.error("Acesso Negado: Apenas o Administrador Master pode acessar este programa.")
    st.stop()

# --- 3. TELA DE CONTROLE ---
tab1, tab2, tab3 = st.tabs(["🔑 GESTÃO DE CHAVES", "📜 LOGS DE ACESSO", "👤 USUÁRIOS"])

with tab1:
    st.write("### Controle de Dispositivos e Locais")
    st.info("As chaves abaixo permitem que o sistema seja aberto em diferentes computadores.")
    
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        with st.container(border=True):
            st.write("#### Criar Nova Chave")
            nova_desc = st.text_input("Destino (Ex: Filial 02, PC Financeiro)")
            novo_codigo = st.text_input("Código de Acesso", placeholder="EX: CHAVE-2024-XYZ")
            if st.button("ATIVAR CHAVE", use_container_width=True, type="primary"):
                if nova_desc and novo_codigo:
                    try:
                        from datetime import datetime
                        executar_comando("INSERT INTO chaves_acesso (codigo, descricao, data_criacao) VALUES (?, ?, ?)", 
                                       (novo_codigo, nova_desc, datetime.now().strftime("%d/%m/%Y %H:%M")))
                        st.success("Chave ativada com sucesso!")
                        st.rerun()
                    except:
                        st.error("Erro: Este código já está em uso.")
                else:
                    st.warning("Preencha todos os campos.")

    with col_c2:
        df_keys = buscar_dados("SELECT id, codigo, descricao, status, data_criacao FROM chaves_acesso ORDER BY id DESC")
        if not df_keys.empty:
            for _, k in df_keys.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.markdown(f"**{k['codigo']}**")
                    c1.caption(f"Criada em: {k['data_criacao']}")
                    c2.write(f"📍 {k['descricao']}")
                    
                    if k['status'] == 1:
                        if c3.button("BLOQUEAR", key=f"blk_{k['id']}", use_container_width=True):
                            executar_comando("UPDATE chaves_acesso SET status = 0 WHERE id = ?", (k['id'],))
                            st.rerun()
                    else:
                        if c3.button("LIBERAR", key=f"unl_{k['id']}", use_container_width=True, type="primary"):
                            executar_comando("UPDATE chaves_acesso SET status = 1 WHERE id = ?", (k['id'],))
                            st.rerun()

with tab2:
    st.write("### Histórico de Auditoria")
    if st.button("🗑️ Limpar Todos os Logs"):
        executar_comando("DELETE FROM logs_acesso")
        st.rerun()
        
    df_logs = buscar_dados("SELECT * FROM logs_acesso ORDER BY id DESC LIMIT 200")
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro de acesso encontrado.")

with tab3:
    st.write("### Gestão de Contas de Usuários")
    df_users = buscar_dados("SELECT id, usuario FROM usuarios")
    st.dataframe(df_users, use_container_width=True)
    
    with st.expander("Adicionar Novo Operador"):
        nu = st.text_input("Nome de Usuário")
        np = st.text_input("Senha")
        if st.button("CADASTRAR"):
            if nu and np:
                executar_comando("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (nu, np))
                st.success("Operador cadastrado!")
                st.rerun()

st.sidebar.button("🚪 Sair do Sistema", on_click=lambda: st.session_state.update({"admin_master": False}))
st.sidebar.markdown("---")
st.sidebar.caption("SISTEMA DE SEGURANÇA EXTERNO V1.0")
