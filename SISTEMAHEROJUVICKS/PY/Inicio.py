# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys

# Adiciona a raiz do projeto ao sys.path para garantir que 'utils' e 'database' sejam encontrados
if getattr(sys, 'frozen', False):
    base = sys._MEIPASS
    internal_py = os.path.join(base, "_internal", "PY")
    sys.path.append(base)
    if os.path.exists(internal_py):
        sys.path.append(internal_py)
else:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import base64
from database import inicializar_banco, buscar_dados, contar_registros, executar_comando
from utils.license_manager import verificar_licenca

# --- 1. CONFIGURAÇÕES DINÂMICAS ---
from utils.auth_manager import (
    verificar_autenticacao, excluir_sessao, obter_dados_empresa, 
    registrar_acesso_salvo, tem_permissao, esquecer_perfil_browser
)
from TEMAS.moderno import apply_modern_style

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
# Obtemos logo e dados da empresa primeiro para configurar a guia do navegador
try:
    nome_empresa, logo_src = obter_dados_empresa()
    # 1. Tenta usar o logo do banco de dados (ajustado pelo usuario)
    if logo_src and "base64," in logo_src:
        import base64 as _b64
        import io as _io
        from PIL import Image as _PIL
        _img_data = _b64.b64decode(logo_src.split("base64,")[1])
        _page_ico = _PIL.open(_io.BytesIO(_img_data))
    else:
        # 2. Fallback para o icone oficial da pasta ICONE
        import os as _os
        from PIL import Image as _PIL
        _ico_png = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "ICONE", "icone.png")
        if _os.path.exists(_ico_png):
            _page_ico = _PIL.open(_ico_png)
        else:
            _page_ico = "👤"
except:
    nome_empresa = "Sistema"
    _page_ico = "👤"
    logo_src = None

st.set_page_config(page_title=f"Dashboard | {nome_empresa}", layout="wide", page_icon=_page_ico)

# ─── 0. VERIFICAÇÃO DE LICENÇA ───
verificar_licenca()

# --- 3. GESTÃO DE ACESSO ---
verificar_autenticacao()

# Garante que se o usuário marcou "Salvar", os dados sejam renovados no LocalStorage/Hardware
registrar_acesso_salvo()

# Aplica o estilo global moderno com o logo no topo
apply_modern_style(logo_url=logo_src)

inicializar_banco()

# --- 4. TELA INICIAL (DASHBOARD) ---
st.sidebar.markdown(f"### 👤 {st.session_state.usuario_nome}")
col_sair1, col_sair2 = st.sidebar.columns(2)
with col_sair1:
    if st.button("🔄 Trocar", help="Trocar de conta (volta ao seletor)", use_container_width=True):
        u = st.session_state.get("usuario_nome")
        excluir_sessao()
        if u: esquecer_perfil_browser(u)
        st.query_params["logout"] = "1"
        st.rerun()
with col_sair2:
    if st.button("🚪 Sair", help="Encerrar e limpar sessão atual", use_container_width=True):
        u = st.session_state.get("usuario_nome")
        excluir_sessao()
        if u: esquecer_perfil_browser(u)
        st.query_params["logout"] = "1"
        st.rerun()

st.sidebar.divider()
if st.sidebar.button("🛑 DESLIGAR SISTEMA", help="Encerra o motor do sistema e libera as portas do computador.", use_container_width=True, type="primary"):
    st.sidebar.warning("Encerrando ecossistema... A janela fechará em instantes.")
    
    # ── LOGICA DE DESLIGAMENTO DESKTOP ──
    js_shutdown = """
        <script>
        // Tenta fechar a janela do navegador
        try {
            window.parent.close();
            window.close();
        } catch(e) {}
        </script>
    """
    st.components.v1.html(js_shutdown, height=0)
    
    import time
    time.sleep(1) # Tempo para o JS tentar fechar
    
    try:
        import psutil
        import os
        
        # 1. Mata o processo atual e todos os filhos (Streamlit, Flask, Node)
        parent = psutil.Process(os.getpid())
        for child in parent.children(recursive=True):
            child.kill()
        
        # 2. Mata o lançador (Tray Icon)
        # Procuramos por processos que tenham 'SISTEMA' ou 'JUVIKS' no nome
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].upper()
                if 'JUVIKS' in name or 'SISTEMA' in name:
                    proc.kill()
            except: pass
            
        parent.kill()
    except:
        # Fallback se psutil não estiver instalado
        os._exit(0)
    st.stop()

nivel = st.session_state.get("usuario_nivel", "ADMIN")

st.title(f"🏠 Bem-vindo, HERO JUVICKS SERVER")

if nivel == "INSTALADOR":
    st.markdown(f"**Painel do Instalador**")
    st.divider()
    st.info("Seu acesso é restrito à Agenda de Instalações e Produção.")
    if st.button("📅 Abrir Agenda", key="btn_age_inst", use_container_width=True, type="primary"):
        st.switch_page("pages/05_Agenda.py")
    st.stop()

st.markdown(f"Gerencie sua operação de forma ágil e segura.")
st.divider()

# Métricas Rápidas
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Clientes Ativos", contar_registros("clientes"))
c2.metric("Propostas Emitidas", contar_registros("orcamentos"))
c3.metric("Itens no Catálogo", contar_registros("produtos"))
c4.metric("Usuários", contar_registros("usuarios"))

# Assinaturas count (Acesso robusto ao banco secundario)
try:
    import sqlite3 as _sqlite3
    if getattr(sys, 'frozen', False):
        _app_data = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "JUVICKS_DATA")
        _assi_db = os.path.join(_app_data, "assinaturas.db")
    else:
        _assi_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assiname_app", "assinaturas.db")

    if os.path.exists(_assi_db):
        _conn = _sqlite3.connect(_assi_db)
        _assi_count = _conn.execute("SELECT COUNT(*) FROM documents WHERE status='completed'").fetchone()[0]
        _conn.close()
    else:
        _assi_count = 0
except:
    _assi_count = 0
c5.metric("Contratos Assinados", _assi_count)

st.write("#")
st.subheader("🚀 Acesso Rápido")

# Cards de Ação Rápida
a1, a2, a3, a4, a5 = st.columns(5)

with a1:
    with st.container(border=True):
        st.markdown("### 📝 Orçamentos")
        st.write("Crie novas propostas comerciais com cálculos automáticos.")
        if tem_permissao("Orçamentos"):
            if st.button("Novo Orçamento", key="btn_orc", use_container_width=True):
                st.switch_page("pages/02_Gerar_Orcamentos.py")
        else:
            st.info("Acesso Restrito")

with a2:
    with st.container(border=True):
        st.markdown("### 📅 Agenda")
        st.write("Gerencie a fila de produção e agendamentos técnicos.")
        if tem_permissao("Agenda"):
            if st.button("Ver Agenda", key="btn_age", use_container_width=True):
                st.switch_page("pages/05_Agenda.py")
        else:
            st.info("Acesso Restrito")

with a3:
    with st.container(border=True):
        st.markdown("### 📊 Performance")
        st.write("Analise faturamento, lucro e desempenho regional.")
        if tem_permissao("Dashboard"):
            if st.button("Abrir Dashboard", key="btn_dash", use_container_width=True):
                st.switch_page("pages/06_Graficos.py")
        else:
            st.info("Acesso Restrito")

with a4:
    with st.container(border=True):
        st.markdown("### 💰 Financeiro")
        st.write("Lance os custos reais de produção e comprovantes.")
        if tem_permissao("Financeiro"):
            if st.button("Gerir Finanças", key="btn_fin", use_container_width=True):
                st.switch_page("pages/10_Financeiro.py")
        else:
            st.info("Acesso Restrito")

with a5:
    with st.container(border=True):
        st.markdown("### ✍️ Assinaturas")
        st.write("Envie contratos para assinatura digital via WhatsApp.")
        if tem_permissao("Assinaturas"):
            if st.button("Assinaturas", key="btn_assi", use_container_width=True, type="primary"):
                st.switch_page("pages/07_Assinaturas.py")
        else:
            st.info("Acesso Restrito")

st.write("#")
with st.expander("🛠️ Outras Funções"):
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    
    if tem_permissao("Configurações"):
        if col_f1.button("⚙️ Configurações", use_container_width=True): 
             st.switch_page("pages/09_Configuracoes_Sistema.py")
    else:
        col_f1.info("Acesso Restrito")
        
    if tem_permissao("Gerenciar Liberações"):
        if col_f2.button("🔑 Liberações", use_container_width=True): 
             st.switch_page("pages/08_Gerenciar_Liberacoes.py")
    else:
        col_f2.info("Acesso Restrito")
        
    if tem_permissao("Contratos"):
        if col_f3.button("📜 Contratos", use_container_width=True): st.switch_page("pages/04_Gerar_Contratos.py")
    else:
        col_f3.info("Acesso Restrito")
        
    if tem_permissao("Assinaturas"):
        if col_f4.button("✍️ Assinaturas ", use_container_width=True): st.switch_page("pages/07_Assinaturas.py")
    else:
        col_f4.info("Acesso Restrito")
    
    if tem_permissao("Painel de Controle"):
        if col_f5.button("⚙️ Painel de Controle", use_container_width=True, type="primary"):
            st.switch_page("pages/99_Painel_Controle.py")
    else:
        col_f5.info("Acesso Restrito")