import streamlit as st
import os, sys
from datetime import datetime

if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import buscar_dados, executar_comando
from TEMAS.moderno import apply_modern_style
from utils.auth_manager import verificar_autenticacao, verificar_nivel_acesso

st.set_page_config(page_title="Gerenciar Acessos", layout="wide", page_icon="🛡️")
apply_modern_style()
verificar_autenticacao()
verificar_nivel_acesso(["ADMIN", "GERENTE"])

st.title("🛡️ Gerenciar Acessos")

tab_term, tab_ops, tab_logs = st.tabs(["💻 Terminais", "👥 Operadores", "📋 Logs"])


# ══════════════════════════════════════════════════════
# TAB 1 — TERMINAIS
# Cadastro unificado: cria o usuário e o terminal de uma vez.
# ══════════════════════════════════════════════════════
with tab_term:
    c_form, c_lista = st.columns([1, 2], gap="large")

    with c_form:
        with st.container(border=True):
            st.subheader("➕ Liberar Acesso")
            st.caption("Cria o operador e autoriza o terminal de uma só vez.")

            with st.form("f_acesso", clear_on_submit=True):
                novo_usuario = st.text_input("👤 Usuário")
                nova_senha   = st.text_input("🔒 Senha", type="password")
                nova_chave   = st.text_input("🔑 Chave do Terminal", placeholder="Ex: JUV-XXXX-XXXX")

                if st.form_submit_button("✅ CRIAR E LIBERAR", use_container_width=True, type="primary"):
                    if novo_usuario and nova_senha and nova_chave:
                        login = novo_usuario.strip().lower()
                        chave = nova_chave.strip().upper()

                        # 1. Cria o usuário — ignora silenciosamente se já existir
                        usuario_ja_existe = not buscar_dados(
                            "SELECT id FROM usuarios WHERE usuario=?", (login,)
                        ).empty

                        if not usuario_ja_existe:
                            try:
                                executar_comando(
                                    "INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES (?,?,?)",
                                    (login, nova_senha, "VENDEDOR")
                                )
                            except Exception as e:
                                st.error(f"Erro ao criar usuário: {e}")
                                st.stop()

                        # 2. Cria a chave de terminal
                        try:
                            executar_comando(
                                "INSERT INTO chaves_acesso (codigo, usuario, descricao, data_criacao) VALUES (?,?,?,?)",
                                (chave, login, f"Terminal de {login}", datetime.now().strftime("%d/%m/%Y %H:%M"))
                            )
                            msg = "Terminal vinculado ao usuário existente!" if usuario_ja_existe else f"✅ Acesso criado! Usuário: {login}"
                            st.success(f"{msg} | Chave: {chave}")
                            st.rerun()
                        except Exception as e:
                            if "UNIQUE" in str(e).upper():
                                st.error(f"A chave '{chave}' já está em uso por outro terminal.")
                            else:
                                st.error(f"Erro ao liberar terminal: {e}")

                    else:
                        st.warning("Preencha Usuário, Senha e Chave.")

    with c_lista:
        st.subheader("Terminais Autorizados")
        busca = st.text_input("🔍 Pesquisar", placeholder="Nome ou chave...", key="s_term")
        df_k = buscar_dados("SELECT * FROM chaves_acesso ORDER BY id DESC")

        if not df_k.empty and busca:
            df_k = df_k[
                df_k['descricao'].str.contains(busca, case=False, na=False) |
                df_k['codigo'].str.contains(busca, case=False, na=False)
            ]

        if df_k.empty:
            st.info("Nenhum terminal cadastrado.")
        else:
            for _, k in df_k.iterrows():
                status_cor = "#22c55e" if k['status'] == 1 else "#ef4444"
                status_txt = "✅ Ativo" if k['status'] == 1 else "🚫 Bloqueado"
                with st.container(border=True):
                    tc1, tc2, tc3 = st.columns([3, 1, 0.5])
                    with tc1:
                        st.markdown(
                            f"**{k['codigo']}** &nbsp; "
                            f"<span style='color:{status_cor};font-size:.8rem;font-weight:700;'>{status_txt}</span><br>"
                            f"<span style='color:#94a3b8;font-size:.82rem;'>👤 {k['usuario']} · 📍 {k['descricao']}</span>",
                            unsafe_allow_html=True
                        )
                    with tc2:
                        btn_label = "🚫 Bloquear" if k['status'] == 1 else "✅ Liberar"
                        if st.button(btn_label, key=f"tog_{k['id']}", use_container_width=True):
                            executar_comando(
                                "UPDATE chaves_acesso SET status=? WHERE id=?",
                                (0 if k['status'] == 1 else 1, k['id'])
                            )
                            st.rerun()
                    with tc3:
                        if k['codigo'] != 'admin':
                            if st.button("🗑️", key=f"del_k_{k['id']}", use_container_width=True):
                                executar_comando("DELETE FROM chaves_acesso WHERE id=?", (k['id'],))
                                st.rerun()


# ══════════════════════════════════════════════════════
# TAB 2 — OPERADORES
# Apenas ajustar o nível de acesso de cada usuário.
# ══════════════════════════════════════════════════════
with tab_ops:
    c1, c2 = st.columns([1, 2], gap="large")
    
    with c1:
        with st.container(border=True):
            st.subheader("➕ Novo Operador")
            st.caption("Cadastre um novo funcionário no sistema.")
            with st.form("f_novo_op", clear_on_submit=True):
                op_user = st.text_input("👤 Nome de Usuário")
                op_pass = st.text_input("🔒 Senha Provisória", type="password")
                op_nivel = st.selectbox("Nível Inicial", ["VENDEDOR", "GERENTE", "ADMIN"])
                
                if st.form_submit_button("🚀 CADASTRAR OPERADOR", use_container_width=True, type="primary"):
                    if op_user and op_pass:
                        login = op_user.strip().lower()
                        # Verifica se existe
                        if not buscar_dados("SELECT id FROM usuarios WHERE usuario=?", (login,)).empty:
                            st.error(f"O usuário '{login}' já existe!")
                        else:
                            try:
                                executar_comando(
                                    "INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES (?,?,?)",
                                    (login, op_pass, op_nivel)
                                )
                                st.success(f"✅ Operador '{login}' cadastrado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar: {e}")
                    else:
                        st.warning("Preencha o nome e a senha.")

    with c2:
        st.subheader("👥 Operadores Cadastrados")
        st.caption("Ajuste o nível de acesso de cada operador abaixo.")

        df_us = buscar_dados("SELECT id, usuario, nivel_acesso FROM usuarios ORDER BY usuario")

        if df_us.empty:
            st.info("Nenhum operador cadastrado.")
        else:
            NIVEIS    = ["VENDEDOR", "GERENTE", "ADMIN"]
            NIVEL_COR = {"ADMIN": "#ef4444", "GERENTE": "#f59e0b", "VENDEDOR": "#22c55e"}

            for _, u in df_us.iterrows():
                cor = NIVEL_COR.get(u['nivel_acesso'], "#64748b")
                with st.container(border=True):
                    uc1, uc2, uc3, uc4 = st.columns([2, 1.5, 1.5, 0.5])

                    with uc1:
                        st.markdown(
                            f"**{u['usuario'].upper()}** &nbsp; "
                            f"<span style='color:{cor};font-size:.75rem;font-weight:700;'>{u['nivel_acesso']}</span>",
                            unsafe_allow_html=True
                        )

                    with uc2:
                        idx = NIVEIS.index(u['nivel_acesso']) if u['nivel_acesso'] in NIVEIS else 0
                        novo_nivel = st.selectbox(
                            "Nível", NIVEIS,
                            index=idx,
                            key=f"nv_{u['id']}",
                            label_visibility="collapsed"
                        )
                        if novo_nivel != u['nivel_acesso']:
                            executar_comando("UPDATE usuarios SET nivel_acesso=? WHERE id=?", (novo_nivel, u['id']))
                            st.rerun()

                    with uc3:
                        if st.button("🛡️ Acessos", key=f"btn_prm_{u['id']}", use_container_width=True):
                            st.session_state[f"show_prm_{u['id']}"] = not st.session_state.get(f"show_prm_{u['id']}", False)
                            st.rerun()

                    with uc4:
                        if u['usuario'] != 'admin':
                            if st.button("🗑️", key=f"del_u_{u['id']}", use_container_width=True):
                                executar_comando("DELETE FROM usuarios WHERE id=?", (u['id'],))
                                executar_comando("DELETE FROM chaves_acesso WHERE usuario=?", (u['usuario'],))
                                st.rerun()

                    # --- NOVO: GERENCIAMENTO DE ACESSO (MÓDULOS) ---
                    if st.session_state.get(f"show_prm_{u['id']}", False):
                        from utils.auth_manager import MODULOS_SISTEMA, obter_permissoes_usuario, salvar_permissoes_usuario
                        st.markdown("<hr style='opacity:0.2; margin: 10px 0px;'>", unsafe_allow_html=True)
                        st.markdown(f"**Permissões de Módulos para: {u['usuario'].upper()}**")
                        
                        p_atual = obter_permissoes_usuario(u['id'])
                        novas_p = {}
                        
                        mod_cols = st.columns(3)
                        for i, mod in enumerate(MODULOS_SISTEMA):
                            with mod_cols[i % 3]:
                                novas_p[mod] = st.checkbox(mod, value=p_atual.get(mod, True), key=f"chk_{u['id']}_{mod}")
                                
                        if st.button("💾 SALVAR PERMISSÕES", key=f"save_prm_{u['id']}", type="primary"):
                            salvar_permissoes_usuario(u['id'], novas_p)
                            st.success("Acessos atualizados com sucesso!")
                            st.session_state[f"show_prm_{u['id']}"] = False
                            st.rerun()



# ══════════════════════════════════════════════════════
# TAB 3 — LOGS
# ══════════════════════════════════════════════════════
with tab_logs:
    st.subheader("📋 Logs de Acesso")

    df_logs = buscar_dados(
        "SELECT usuario as 'Operador', data_hora as 'Data/Hora', ip as 'IP' "
        "FROM logs_acesso ORDER BY id DESC LIMIT 300"
    )

    if df_logs.empty:
        st.info("Nenhum log registrado.")
    else:
        cl1, cl2 = st.columns([4, 1])
        cl1.caption(f"{len(df_logs)} registros exibidos (últimos 300).")
        with cl2:
            if st.button("🗑️ Limpar Todos os Logs", use_container_width=True, type="secondary"):
                st.session_state["confirmar_limpar_logs"] = True

        if st.session_state.get("confirmar_limpar_logs", False):
            with st.container(border=True):
                st.warning("⚠️ **Atenção:** Esta ação apagará **todos** os registros de acesso permanentemente.")
                cc1, cc2 = st.columns(2)
                if cc1.button("✅ SIM, LIMPAR TUDO", type="primary", use_container_width=True):
                    executar_comando("DELETE FROM logs_acesso")
                    st.session_state["confirmar_limpar_logs"] = False
                    st.success("Logs apagados com sucesso.")
                    st.rerun()
                if cc2.button("❌ Cancelar", use_container_width=True):
                    st.session_state["confirmar_limpar_logs"] = False
                    st.rerun()

        st.dataframe(df_logs, use_container_width=True, hide_index=True)

