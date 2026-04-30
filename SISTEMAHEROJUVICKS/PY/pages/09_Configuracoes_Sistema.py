import streamlit as st
import os
import sys

# Adiciona a raiz do projeto ao sys.path para garantir que 'utils' e 'database' sejam encontrados
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import io
import json
import base64
from datetime import datetime, timedelta
from database import executar_comando, buscar_dados, conectar, DB_PATH
from TEMAS.moderno import apply_modern_style
from utils.auth_manager import (
    verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo, tem_permissao,
    MODULOS_SISTEMA, obter_permissoes_usuario, salvar_permissoes_usuario
)
from utils.query_cache import cached_buscar_dados, get_config_cache_version, bump_config_cache_version

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
# Cache version for config-related queries
config_cache_version = get_config_cache_version()

try:
    df_conf = cached_buscar_dados("SELECT * FROM config LIMIT 1", version=config_cache_version)
    nome_empresa = df_conf.iloc[0]['empresa_nome'] if not df_conf.empty else "Sistema"
    conf = df_conf.iloc[0].to_dict() if not df_conf.empty else {}
except:
    nome_empresa = "JUVICKS"
    df_conf = None
    conf = {}

st.set_page_config(page_title=f"Configurações | {nome_empresa}", layout="wide", page_icon="⚙️")

# LOGIN PROTECTION
verificar_autenticacao()

# Aplica o estilo global moderno com logo
_, logo_src = obter_dados_empresa()
apply_modern_style(logo_url=logo_src)

# ─── 2. SEGURANÇA ───
from utils.auth_manager import verificar_nivel_acesso
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR"])
verificar_permissao_modulo("Configurações")
nivel = st.session_state.get("usuario_nivel", "ADMIN")

# --- CABEÇALHO ---
st.title("⚙️ Painel de Configurações")
st.markdown("""
<div style='background: rgba(245, 166, 35, 0.1); border-left: 4px solid #f5a623; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
    <p style='margin: 0; color: #fbd38d; font-size: 0.95rem;'>
        <b>Gestão do Sistema:</b> Ajuste os parâmetros fundamentais, regras de negócio e integrações da sua plataforma.
    </p>
</div>
""", unsafe_allow_html=True)

# --- LÓGICA DE ABAS ---
abas_nomes = [
    "🏢 IDENTIDADE", 
    "🏗️ ENGENHARIA", 
    "🤝 CONSULTORES", 
    "💳 FINANCEIRO", 
    "🏷️ CATEGORIAS", 
    "📜 CONTRATOS", 
    "📊 BACKUP & DADOS"
]
tabs = st.tabs(abas_nomes)

# --- TAB 0: IDENTIDADE E WHATSAPP ---
with tabs[0]:
    if nivel != "ADMIN":
        st.warning("🚫 Acesso restrito ao Administrador.")
    else:
        # Layout focado apenas em Identidade Institucional
        st.subheader("🏛️ Dados Institucionais")
        st.caption("Informações que aparecem nos orçamentos e contratos.")
        
        with st.container(border=True):
            col_id1, col_id2 = st.columns([1, 2], gap="large")
            
            with col_id1:
                if conf.get('logo_data'):
                    st.image(base64.b64decode(conf['logo_data']), width=220)
                    uploaded_file = st.file_uploader("Trocar Logo", type=['png', 'jpg', 'jpeg'])
                else:
                    st.info("Sem Logo")
                    uploaded_file = st.file_uploader("Subir Logo (JPEG/PNG)", type=['png', 'jpg', 'jpeg'])

            with col_id2:
                c1, c2 = st.columns(2)
                nome_emp = c1.text_input("Razão Social", value=conf.get('empresa_nome', ''))
                cnpj_emp = c2.text_input("CNPJ", value=conf.get('empresa_cnpj') or conf.get('cnpj', ''))
                
                tel_emp = c1.text_input("Telefone Fixo", value=conf.get('empresa_tel') or conf.get('telefone', ''))
                wpp_base = c2.text_input("WhatsApp Suporte", value=conf.get('empresa_whatsapp') or '', help="Número oficial de suporte.")
                
                end_emp = c1.text_input("Endereço (Rua/Logradouro)", value=conf.get('empresa_end') or '')
                num_emp = c2.text_input("Número", value=conf.get('empresa_num') or '')
                
                if st.button("💾 SALVAR ALTERAÇÕES DE IDENTIDADE", type="primary", use_container_width=True):
                    logo_bytes = base64.b64encode(uploaded_file.read()).decode() if uploaded_file else conf.get('logo_data', '')
                    executar_comando("DELETE FROM config")
                    executar_comando("""
                        INSERT INTO config (empresa_nome, empresa_cnpj, empresa_tel, empresa_whatsapp, empresa_end, empresa_num, logo_data) 
                        VALUES (?,?,?,?,?,?,?)
                    """, (nome_emp, cnpj_emp, tel_emp, wpp_base, end_emp, num_emp, logo_bytes))
                    bump_config_cache_version()
                    st.success("Dados Institucionais atualizados com sucesso!")
                    st.rerun()

# --- TAB 1: ENGENHARIA ---
with tabs[1]:
    verificar_permissao_modulo("Config - Engenharia/Produtos")
    st.subheader("🏗️ Engenharia de Portfólio")
    
    df_cat_list = cached_buscar_dados("SELECT nome FROM categorias_produtos ORDER BY nome", version=config_cache_version)
    lista_categorias = df_cat_list['nome'].tolist() if not df_cat_list.empty else ["Geral"]

    t_list, t_new = st.tabs(["🔍 CATÁLOGO ATUAL", "🆕 ENGENHARIA DE PRODUTO"])

    with t_list:
        df_produtos = cached_buscar_dados("SELECT * FROM produtos ORDER BY id DESC", version=config_cache_version)
        if df_produtos.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            c_f1, c_f2 = st.columns([2, 1])
            busca = c_f1.text_input("🔎 Pesquisar item...", key="search_eng_p")
            
            df_view = df_produtos
            if busca:
                df_view = df_produtos[df_produtos['nome'].str.contains(busca, case=False, na=False)]
            
            for _, p in df_view.iterrows():
                with st.container(border=True):
                    cp1, cp2, cp3 = st.columns([1, 2.5, 1])
                    
                    with cp1:
                        if p.get('img_data'):
                            st.image(base64.b64decode(p['img_data']), use_container_width=True)
                        else:
                            st.markdown("<div style='background:#1e293b; height:100px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#475569;'>📦 Sem Foto</div>", unsafe_allow_html=True)
                    
                    with cp2:
                        st.markdown(f"#### {p['nome']}")
                        st.markdown(f"🏷️ `{p['categoria']}` | 📏 Unidade: `{p['unidade']}`")
                        st.caption(p['descricao'] or "Sem descrição técnica.")
                    
                    with cp3:
                        st.write("") # Spacer
                        st.metric("Preço de Venda", f"R$ {p['preco']:,.2f}")
                        if st.button("🔧 Detalhes/Editar", key=f"ed_eng_{p['id']}", use_container_width=True):
                            st.session_state[f"exp_eng_{p['id']}"] = not st.session_state.get(f"exp_eng_{p['id']}", False)
                            st.rerun()

                    if st.session_state.get(f"exp_eng_{p['id']}", False):
                        st.markdown("---")
                        ed_c1, ed_c2 = st.columns([2, 1])
                        with ed_c1:
                            comp = json.loads(p['composicao_json']) if p['composicao_json'] else [{"Item": "", "Custo (R$)": 0.0}]
                            st.markdown("**Composição (BOM):**")
                            new_bom = st.data_editor(pd.DataFrame(comp), num_rows="dynamic", use_container_width=True, key=f"bom_ed_{p['id']}")
                        with ed_c2:
                            st.markdown("**Valores Unitários:**")
                            new_venda = st.number_input("Valor de Venda (R$)", value=float(p['preco']), key=f"vend_ed_{p['id']}")
                            new_proc = st.number_input("Mão de Obra (R$)", value=float(p['custo_processamento'] or 0), key=f"proc_ed_{p['id']}")
                            
                            c_total = new_bom["Custo (R$)"].sum() + new_proc
                            st.info(f"Custo Total: R$ {c_total:,.2f}")
                            
                            if st.button("💾 Salvar Alterações", key=f"save_eng_{p['id']}", type="primary", use_container_width=True):
                                bom_json = json.dumps([i for i in new_bom.to_dict('records') if i['Item']])
                                executar_comando("UPDATE produtos SET preco=?, custo_processamento=?, composicao_json=? WHERE id=?", 
                                               (new_venda, new_proc, bom_json, p['id']))
                                st.success("Atualizado!")
                                st.rerun()

    with t_new:
        with st.container(border=True):
            st.subheader("📝 Ficha de Engenharia")
            with st.form("form_novo_prod_eng", clear_on_submit=True):
                n1, n2, n3 = st.columns([3, 1, 1])
                nome_n = n1.text_input("Descrição Comercial *")
                cat_n = n2.selectbox("Categoria", lista_categorias)
                un_n = n3.selectbox("Unidade", ["Unid", "M²", "M", "Kg"])
                
                st.markdown("**Lista de Materiais e Insumos (BOM)**")
                bom_n = st.data_editor(pd.DataFrame([{"Item": "", "Custo (R$)": 0.0}]), num_rows="dynamic", use_container_width=True)
                
                v1, v2, v3 = st.columns(3)
                proc_n = v1.number_input("Mão de Obra (R$)", min_value=0.0)
                depr_n = v2.number_input("Depreciação (R$)", min_value=0.0)
                venda_n = v3.number_input("Preço Sugerido (R$)", min_value=0.0)
                
                img_n = st.file_uploader("Foto Técnica", type=['jpg', 'jpeg', 'png'])
                
                if st.form_submit_button("🚀 CADASTRAR PRODUTO", use_container_width=True):
                    if nome_n:
                        img_s = base64.b64encode(img_n.read()).decode() if img_n else ""
                        bom_s = json.dumps([i for i in bom_n.to_dict('records') if i['Item']])
                        executar_comando("INSERT INTO produtos (nome, categoria, unidade, preco, custo_processamento, depreciacao, composicao_json, img_data) VALUES (?,?,?,?,?,?,?,?)",
                                       (nome_n, cat_n, un_n, venda_n, proc_n, depr_n, bom_s, img_s))
                        st.success("Produto ativado!")
                        st.rerun()

# --- TAB 2: CONSULTORES ---
with tabs[2]:
    st.subheader("🤝 Gestão de Consultores / Vendedores")
    
    col_v1, col_v2 = st.columns([1, 1.5], gap="large")
    
    with col_v1:
        with st.container(border=True):
            st.subheader("➕ Novo Consultor")
            nv_nome = st.text_input("Nome Completo", key="new_v_name")
            if st.button("✨ CADASTRAR CONSULTOR", use_container_width=True, type="primary"):
                if nv_nome:
                    executar_comando("INSERT INTO vendedores (nome) VALUES (?)", (nv_nome.strip(),))
                    bump_config_cache_version()
                    st.success("Consultor cadastrado!")
                    st.rerun()
    
    with col_v2:
        df_v = cached_buscar_dados("SELECT * FROM vendedores ORDER BY nome", version=config_cache_version)
        if df_v.empty:
            st.info("Nenhum consultor ativo.")
        else:
            for _, v in df_v.iterrows():
                with st.container(border=True):
                    vc1, vc2 = st.columns([3, 1])
                    vc1.markdown(f"**👤 {v['nome']}**")
                    if v['nome'] != 'Admin':
                        if vc2.button("🗑️ Remover", key=f"del_v_{v['id']}", use_container_width=True):
                            executar_comando("DELETE FROM vendedores WHERE id=?", (v['id'],))
                            bump_config_cache_version()
                            st.success("Vendedor removido!")
                            st.rerun()

# --- TAB 3: FINANCEIRO ---
with tabs[3]:
    st.subheader("💳 Regras Financeiras e Pagamento")
    col_f1, col_f2 = st.columns([1, 1.5], gap="large")
    
    with col_f1:
        with st.container(border=True):
            st.subheader("➕ Nova Regra")
            with st.form("form_nova_fp", clear_on_submit=True):
                f_nome = st.text_input("Nome (ex: Pix, Cartão 12x)")
                f_tipo = st.selectbox("Tipo", ["À Vista", "Cartão", "Boleto", "Outros"])
                f_taxa = st.number_input("Taxa/Juros (%)", min_value=0.0, step=0.1)
                f_parc = st.number_input("Qtd Máx Parcelas", min_value=1, max_value=36, value=1)
                
                if st.form_submit_button("✨ CADASTRAR REGRA", use_container_width=True):
                    if f_nome:
                        executar_comando("INSERT INTO formas_pagamento (nome, tipo, taxa, qtd_parcelas) VALUES (?,?,?,?)",
                                       (f_nome.strip(), f_tipo, f_taxa, f_parc))
                        bump_config_cache_version()
                        st.success("Regra financeira cadastrada!")
                        st.rerun()

    with col_f2:
        df_fp = cached_buscar_dados("SELECT * FROM formas_pagamento ORDER BY id DESC", version=config_cache_version)
        if df_fp.empty:
            st.info("Nenhuma regra de pagamento definida.")
        else:
            for _, f in df_fp.iterrows():
                with st.container(border=True):
                    fc1, fc2, fc3 = st.columns([2, 1, 1])
                    fc1.markdown(f"**💳 {f['nome']}**")
                    fc1.caption(f"Tipo: {f['tipo']} | Juros/Taxa: {f['taxa']}%")
                    
                    fc2.write(f"{f['qtd_parcelas']}x" if f['tipo'] == 'Cartão' else "À Vista")
                    if fc3.button("🗑️", key=f"del_f_{f['id']}", use_container_width=True):
                        executar_comando("DELETE FROM formas_pagamento WHERE id=?", (f['id'],))
                        bump_config_cache_version()
                        st.rerun()

# --- TAB 4: CATEGORIAS ---
with tabs[4]:
    st.subheader("🏷️ Categorias de Produtos")
    c_cat1, c_cat2 = st.columns([1, 1])
    
    with c_cat1:
        with st.form("cad_cat_v2"):
            n_cat = st.text_input("Nova Categoria")
            if st.form_submit_button("➕ ADICIONAR", use_container_width=True):
                if n_cat:
                    # Verificação agnóstica de existência
                    exists = buscar_dados("SELECT 1 FROM categorias_produtos WHERE nome = ?", (n_cat.strip(),))
                    if exists.empty:
                        executar_comando("INSERT INTO categorias_produtos (nome) VALUES (?)", (n_cat.strip(),))
                        bump_config_cache_version()
                        st.rerun()
                    else:
                        st.warning("Esta categoria já existe.")
                    
    with c_cat2:
        df_c = cached_buscar_dados("SELECT * FROM categorias_produtos ORDER BY nome", version=config_cache_version)
        for _, c in df_c.iterrows():
            with st.container(border=True):
                cc1, cc2 = st.columns([3, 1])
                cc1.write(f"📁 **{c['nome']}**")
                if cc2.button("🗑️", key=f"del_c_{c['id']}"):
                    executar_comando("DELETE FROM categorias_produtos WHERE id=?", (c['id'],))
                    bump_config_cache_version()
                    st.rerun()

# --- TAB 5: CONTRATOS ---
with tabs[5]:
    st.subheader("📜 Modelos de Documentação")
    with st.expander("ℹ️ Guia de Tags Avançado"):
        st.info("Copie e cole as tags corretas abaixo no seu arquivo Word (.docx). Elas serão substituídas automaticamente pelo sistema na geração do contrato.")
        c_tag1, c_tag2, c_tag3 = st.columns(3)
        with c_tag1:
            st.markdown("**👤 Dados do Cliente**")
            st.caption("{{cliente_nome}} ou [NOME DO CLIENTE]")
            st.caption("{{cliente_cnpj}} ou [CPF/CNPJ DO CLIENTE]")
            st.caption("{{cliente_endereco}}")
            st.caption("{{cliente_numero}}")
            st.caption("{{cliente_bairro}}")
            st.caption("{{cliente_cidade}}")
            st.caption("{{cliente_uf}}")
            st.caption("{{cliente_cep}}")
            st.caption("{{cliente_telefone}}")
            st.caption("{{cliente_email}}")
        with c_tag2:
            st.markdown("**💰 Venda e Produtos**")
            st.caption("{{numero_orcamento}} ou {{id_orcamento}}")
            st.caption("{{valor_total}}")
            st.caption("{{valor_extenso}}")
            st.caption("{{forma_pagamento}}")
            st.caption("{{financeiro_obs}}")
            st.caption("{{prazo_entrega}}")
            st.caption("{{itens_orcamento}}")
            st.caption("{{descricao_itens}}")
            st.caption("{{vendedor}}")
        with c_tag3:
            st.markdown("**🏢 Sua Empresa**")
            st.caption("{{empresa_nome}} ou [NOME DA SUA EMPRESA]")
            st.caption("{{empresa_cnpj}} ou [SEU CNPJ]")
            st.caption("{{empresa_endereco}}")
            st.caption("{{empresa_numero}}")
            st.caption("{{empresa_telefone}}")
            st.markdown("**📅 Data do Contrato**")
            st.caption("{{dia}}")
            st.caption("{{mes}}")
            st.caption("{{ano}}")
            st.caption("{{data_por_extenso}}")
        
    with st.form("cad_contrato", clear_on_submit=True):
        m_nome = st.text_input("Nome do Template")
        m_file = st.file_uploader("Upload .docx", type=['docx'])
        if st.form_submit_button("📄 SALVAR TEMPLATE", use_container_width=True):
            if m_nome and m_file:
                executar_comando("INSERT OR REPLACE INTO modelos_contrato (nome, arquivo_bin) VALUES (?,?)", (m_nome.strip(), m_file.read()))
                bump_config_cache_version()
                st.rerun()
                
    st.markdown("---")
    df_m = cached_buscar_dados("SELECT id, nome FROM modelos_contrato", version=config_cache_version)
    for _, m in df_m.iterrows():
        with st.container(border=True):
            mc1, mc2 = st.columns([4, 1])
            mc1.write(f"📄 **{m['nome']}**")
            if mc2.button("🗑️", key=f"del_m_{m['id']}"):
                executar_comando("DELETE FROM modelos_contrato WHERE id=?", (m['id'],))
                bump_config_cache_version()
                st.rerun()

# --- TAB 6: BACKUP & DADOS ---
with tabs[6]:
    verificar_permissao_modulo("Config - Backup/Dados")
    st.subheader("📊 Central de Dados e Backup")
    
    b_col1, b_col2 = st.columns(2, gap="large")
    
    with b_col1:
            with st.container(border=True):
                st.markdown("#### 💾 Backup de Segurança")
                st.caption("Baixe uma cópia completa do banco de dados para segurança externa.")
                if os.path.exists(DB_PATH):
                    with open(DB_PATH, "rb") as f:
                        st.download_button("📥 DESCARREGAR BANCO (.DB)", f, file_name=f"backup_juvicks_{datetime.now().strftime('%d_%m_%Y')}.db", type="primary", use_container_width=True)
                
                st.markdown("---")
                st.markdown("#### 📤 Restaurar Banco de Dados (.DB)")
                st.caption("⚠️ ATENÇÃO: Isso irá SUBSTITUIR todos os seus dados atuais pelo arquivo enviado.")
                
                up_db = st.file_uploader("Selecione o arquivo .db de backup", type=['db'], key="up_db_restore")
                if up_db is not None:
                    if st.button("🚀 CONFIRMAR RESTAURAÇÃO E REINICIAR", type="primary", use_container_width=True):
                        try:
                            import shutil
                            # 1. Faz backup do atual por seguranca
                            if os.path.exists(DB_PATH):
                                shutil.copy2(DB_PATH, DB_PATH + ".bak")
                            
                            # 2. Salva o novo banco
                            with open(DB_PATH, "wb") as f:
                                f.write(up_db.getbuffer())
                            
                            st.success("✅ Banco de dados restaurado com sucesso!")
                            st.info("Reiniciando sistema para aplicar mudanças...")
                            import time
                            time.sleep(2)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro crítico ao restaurar: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📑 Importação de Planilhas")
            cat_imp = st.selectbox("Escolha onde importar:", ["clientes", "produtos", "orcamentos"])
            file_imp = st.file_uploader("Arquivo Excel ou CSV", type=['xlsx', 'csv'])
            if file_imp and st.button("🚀 INICIAR IMPORTAÇÃO", use_container_width=True):
                # ... logica de importação simplificada ...
                st.info("Processando dados...")
                try:
                    df = pd.read_csv(file_imp) if file_imp.name.endswith('.csv') else pd.read_excel(file_imp)
                    st.success(f"Capturados {len(df)} registros. Processando...")
                except: st.error("Erro no formato do arquivo.")

    with b_col2:
        with st.container(border=True):
            st.markdown("#### 📉 Exportação Rápida")
            cat_exp = st.selectbox("Escolha o que exportar:", ["clientes", "produtos", "orcamentos", "formas_pagamento"])
            if st.button("📊 GERAR PLANILHA", use_container_width=True):
                df_ee = buscar_dados(f"SELECT * FROM {cat_exp}")
                if not df_ee.empty:
                    csv = df_ee.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 BAIXAR CSV", csv, f"{cat_exp}_export.csv", "text/csv", use_container_width=True)
                else: st.warning("Sem dados para exportar.")

st.sidebar.markdown("---")
st.sidebar.caption("SISTEMA JUVIKS | CONFIG V11.0")
