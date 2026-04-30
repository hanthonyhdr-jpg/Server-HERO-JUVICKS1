import streamlit as st
import os
import sys
import re
import requests

# Adiciona a raiz do projeto ao sys.path para garantir que 'utils' e 'database' sejam encontrados
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
import base64
from datetime import datetime, timedelta
from database import buscar_dados, executar_comando
from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, obter_dados_empresa, verificar_permissao_modulo
from utils.query_cache import cached_buscar_dados, get_clientes_cache_version, bump_clientes_cache_version

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
# Usamos cache para obter metadados da empresa e ícone
nome_empresa, logo_src = obter_dados_empresa()
st.set_page_config(page_title=f"Clientes | {nome_empresa}", layout="wide", page_icon="👤")

# Aplica o estilo global moderno (já otimizado com cache no auth_manager)
apply_modern_style(logo_url=logo_src)

# --- LOGIN PROTECTION ---
verificar_autenticacao()
from utils.auth_manager import verificar_nivel_acesso
verificar_nivel_acesso(["ADMIN", "GERENTE", "VENDEDOR"])
verificar_permissao_modulo("Clientes")

# --- 4. FUNÇÕES AUXILIARES OTIMIZADAS ---
@st.cache_resource
def inicializar_schema_clientes():
    """Garante as colunas necessárias apenas uma vez por execução do servidor."""
    colunas = [("nome_fantasia", "TEXT"), ("inscricao_estadual", "TEXT"),
               ("estado", "TEXT"), ("cidade", "TEXT"), ("bairro", "TEXT"), ("telefone", "TEXT"),
               ("email", "TEXT"), ("numero", "TEXT"), ("cep", "TEXT")]
    for col, tipo in colunas:
        try: executar_comando(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}")
        except: pass

UFS_BRASIL = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
              'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

def gerar_novo_id_cliente():
    df_ids = cached_buscar_dados("SELECT id FROM clientes WHERE id LIKE 'CLI-%'", version=clientes_cache_version)
    numeros = []
    if not df_ids.empty:
        for id_existente in df_ids['id']:
            try:
                num = int(id_existente.split('-')[1])
                numeros.append(num)
            except (IndexError, ValueError):
                continue
    novo_num = max(numeros) + 1 if numeros else 1
    return f"CLI-{novo_num:03d}"


def limpar_clientes_incompletos():
    cleanup_key = "clientes_cleanup_done_version"
    current_version = get_clientes_cache_version()
    if st.session_state.get(cleanup_key) == current_version:
        return

    df_invalid = buscar_dados("SELECT COUNT(*) AS total FROM clientes WHERE nome IS NULL OR TRIM(nome) = '' OR id IS NULL")
    total_invalid = int(df_invalid.iloc[0]['total']) if not df_invalid.empty else 0
    if total_invalid > 0:
        executar_comando("DELETE FROM clientes WHERE nome IS NULL OR TRIM(nome) = '' OR id IS NULL")
        bump_clientes_cache_version()

    st.session_state[cleanup_key] = get_clientes_cache_version()

def buscar_dados_cnpj(cnpj):
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    if len(cnpj_limpo) == 14:
        try:
            url = f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                dados = response.json()
                est = dados.get('estabelecimento', {})
                st.session_state.t_nome = dados.get('razao_social', '')
                st.session_state.t_fantasia = est.get('nome_fantasia', '') or dados.get('nome_fantasia', '')
                st.session_state.t_end = f"{est.get('tipo_logradouro', '')} {est.get('logradouro', '')}".strip()
                st.session_state.t_num = est.get('numero', '')
                st.session_state.t_cep = est.get('cep', '')
                st.session_state.t_uf = est.get('estado', {}).get('sigla', '')
                st.session_state.t_cid = est.get('cidade', {}).get('nome', '')
                st.session_state.t_tel = est.get('ddd1', '') + est.get('telefone1', '')
                st.session_state.t_email = est.get('email', '')
                return True
        except: pass
    return False

# Executa a inicialização do schema uma única vez (cacheado)
inicializar_schema_clientes()
limpar_clientes_incompletos()
clientes_cache_version = get_clientes_cache_version()

# --- 5. TÍTULO ---
st.title("👤 Relacionamento com Clientes")
st.markdown("---")

# --- 6. NAVEGAÇÃO (radio em vez de tabs para permitir troca via código) ---
campos_state = ['t_nome', 't_fantasia', 't_cnpj', 't_ins', 't_end', 't_num',
                't_cep', 't_uf', 't_cid', 't_bairro', 't_tel', 't_email']

for key in campos_state:
    if key not in st.session_state:
        st.session_state[key] = ""

if 'aba_ativa' not in st.session_state:
    st.session_state.aba_ativa = "➕ Novo Registro"

escolha = st.radio(
    "Ação:", ["➕ Novo Registro", "👥 Base de Contatos"],
    index=0 if st.session_state.aba_ativa == "➕ Novo Registro" else 1,
    horizontal=True, label_visibility="collapsed"
)
st.session_state.aba_ativa = escolha
st.write("")

# ========== ABA 1: NOVO REGISTRO / EDIÇÃO ==========
if st.session_state.aba_ativa == "➕ Novo Registro":
    edit_id = st.session_state.get('edit_client_id')

    if edit_id:
        st.info(f"✏️ Editando cliente: **{st.session_state.t_nome}** (ID: {edit_id})")

    # Busca rápida de CNPJ
    with st.container(border=True):
        st.markdown("#### ⚡ Registro Rápido (CNPJ)")
        c_busca1, c_busca2 = st.columns([3, 1])
        cnpj_input = c_busca1.text_input("CNPJ da Empresa", placeholder="00.000.000/0000-00", label_visibility="collapsed")
        if c_busca2.button("🔍 Importar Dados", use_container_width=True, type="primary"):
            if buscar_dados_cnpj(cnpj_input):
                st.success("Dados importados com sucesso!")
                st.rerun()
            else:
                st.error("CNPJ não encontrado.")

    # Formulário de Cadastro/Edição
    with st.form("ficha_cliente", clear_on_submit=True):
        st.write("### 📄 Ficha Cadastral")

        f_nome = st.text_input("Razão Social *", value=st.session_state.t_nome)
        f_fantasia = st.text_input("Nome Fantasia", value=st.session_state.t_fantasia)

        c1, c2 = st.columns(2)
        # Ao editar, usa o cnpj do estado; no cadastro novo, usa o campo de busca ou vazio
        v_cnpj = st.session_state.t_cnpj if edit_id else (cnpj_input if cnpj_input else "")
        f_cnpj = c1.text_input("CPF/CNPJ *", value=v_cnpj)
        f_ins = c2.text_input("Inscrição Estadual (IE)", value=st.session_state.t_ins)

        st.divider()
        st.write("📍 Localização")
        c_end, c_num, c_cep = st.columns([3, 1, 1])
        f_end = c_end.text_input("Endereço / Logradouro", value=st.session_state.t_end)
        f_num = c_num.text_input("Nº", value=st.session_state.t_num)
        f_cep = c_cep.text_input("CEP", value=st.session_state.t_cep)

        c3, c4, c5, c6 = st.columns([1, 2, 2, 2])
        idx_uf = UFS_BRASIL.index(st.session_state.t_uf) if st.session_state.t_uf in UFS_BRASIL else 0
        f_est = c3.selectbox("UF", UFS_BRASIL, index=idx_uf)
        f_cid = c4.text_input("Cidade", value=st.session_state.t_cid)
        f_bai = c5.text_input("Bairro", value=st.session_state.t_bairro)
        f_tel = c6.text_input("Telefone Principal", value=st.session_state.t_tel)

        f_email = st.text_input("E-mail para Faturamento", value=st.session_state.t_email)

        st.write("")

        if edit_id:
            col_save, col_cancel = st.columns(2)
            salvar = col_save.form_submit_button("📝 SALVAR ALTERAÇÕES", use_container_width=True, type="primary")
            cancelar = col_cancel.form_submit_button("❌ CANCELAR", use_container_width=True)

            if salvar:
                if f_nome and f_cnpj:
                    executar_comando("""
                        UPDATE clientes SET nome=?, nome_fantasia=?, cnpj=?, inscricao_estadual=?,
                        endereco=?, numero=?, cep=?, estado=?, cidade=?, bairro=?, telefone=?, email=?
                        WHERE id=?
                    """, (f_nome, f_fantasia, f_cnpj, f_ins, f_end, f_num, f_cep,
                          f_est, f_cid, f_bai, f_tel, f_email, edit_id))
                    bump_clientes_cache_version()
                    st.success(f"✅ Cliente '{f_nome}' atualizado!")
                    for key in campos_state: st.session_state[key] = ""
                    if 'edit_client_id' in st.session_state: del st.session_state['edit_client_id']
                    st.session_state.aba_ativa = "👥 Base de Contatos"
                    st.rerun()
                else:
                    st.warning("Razão Social e CPF/CNPJ são obrigatórios.")

            if cancelar:
                for key in campos_state: st.session_state[key] = ""
                if 'edit_client_id' in st.session_state: del st.session_state['edit_client_id']
                st.session_state.aba_ativa = "👥 Base de Contatos"
                st.rerun()
        else:
            if st.form_submit_button("✅ SALVAR E ATIVAR CLIENTE", use_container_width=True, type="primary"):
                if f_nome and f_cnpj:
                    novo_id = gerar_novo_id_cliente()
                    executar_comando("""
                        INSERT INTO clientes (id, nome, nome_fantasia, cnpj, inscricao_estadual,
                        endereco, numero, cep, estado, cidade, bairro, telefone, email)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (novo_id, f_nome, f_fantasia, f_cnpj, f_ins, f_end, f_num, f_cep,
                          f_est, f_cid, f_bai, f_tel, f_email))
                    bump_clientes_cache_version()
                    st.success(f"Cliente '{f_nome}' cadastrado com ID {novo_id}!")
                    for key in campos_state: st.session_state[key] = ""
                    st.rerun()
                else:
                    st.warning("Razão Social e CPF/CNPJ são obrigatórios.")

# ========== ABA 2: BASE DE CONTATOS ==========
else:
    c_g1, c_g2 = st.columns([2, 1])
    with c_g1:
        termo = st.text_input("🔎 Pesquisar na Base", placeholder="Nome, CNPJ ou Cidade...")
    with c_g2:
        ordem = st.selectbox("Ordenar por:", ["id DESC", "nome ASC", "cidade ASC"],
                             format_func=lambda x: x.split(" ")[0].upper())

    where_sql = ""
    params = ()
    termo = termo.strip()
    if termo:
        termo_like = f"%{termo}%"
        where_sql = "WHERE nome LIKE ? OR cnpj LIKE ? OR cidade LIKE ? OR estado LIKE ? OR email LIKE ? OR telefone LIKE ? OR id LIKE ?"
        params = (termo_like, termo_like, termo_like, termo_like, termo_like, termo_like, termo_like)

    df = cached_buscar_dados(
        f"SELECT * FROM clientes {where_sql} ORDER BY {ordem}",
        params,
        version=clientes_cache_version
    )

    if not df.empty:
        st.write(f"**{len(df)}** clientes encontrados")

        for idx, row in df.iterrows():
            cid_info = f" | {row.get('cidade', '')}-{row.get('estado', '')}" if row.get('cidade') else ""
            id_comp = str(row['id']) if row['id'] else f"TEMP-{idx}"
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1.5, 0.5, 0.5])
                with c1:
                    st.markdown(f"**{row['nome']}**")
                    st.caption(f"ID: {id_comp} | CNPJ/CPF: {row.get('cnpj', '')}{cid_info}")
                with c2:
                    st.caption(f"📞 {row.get('telefone', '')}")
                    st.caption(f"✉️ {row.get('email', '')}")

                if c3.button("📝", key=f"edit_{id_comp}_{idx}", help="Editar Cliente"):
                    st.session_state.edit_client_id = row['id']
                    st.session_state.t_nome = row.get('nome', '')
                    st.session_state.t_fantasia = row.get('nome_fantasia', '')
                    st.session_state.t_cnpj = row.get('cnpj', '')
                    st.session_state.t_ins = row.get('inscricao_estadual', '')
                    st.session_state.t_end = row.get('endereco', '')
                    st.session_state.t_num = row.get('numero', '')
                    st.session_state.t_cep = row.get('cep', '')
                    st.session_state.t_uf = row.get('estado', '')
                    st.session_state.t_cid = row.get('cidade', '')
                    st.session_state.t_bairro = row.get('bairro', '')
                    st.session_state.t_tel = row.get('telefone', '')
                    st.session_state.t_email = row.get('email', '')
                    st.session_state.aba_ativa = "➕ Novo Registro"
                    st.rerun()

                if c4.button("🗑️", key=f"del_{id_comp}_{idx}", help="Excluir Cliente"):
                    if row['id']:
                        executar_comando("DELETE FROM clientes WHERE id=?", (row['id'],))
                        bump_clientes_cache_version()
                    st.success("Cliente removido!")
                    st.rerun()
    else:
        st.info("Nenhum cliente encontrado.")
