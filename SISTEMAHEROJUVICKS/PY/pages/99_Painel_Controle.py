import streamlit as st
import os
import sys
import sqlite3
import shutil
import base64
import subprocess
import requests
from datetime import datetime

# Adiciona a raiz do projeto ao sys.path
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from database import buscar_dados, executar_comando, DB_PATH, inicializar_banco, DATA_DIR
from utils.auth_manager import verificar_autenticacao, verificar_nivel_acesso, verificar_permissao_modulo, tem_permissao, obter_dados_empresa
from utils.hardware_license import registrar_computador
from TEMAS.moderno import apply_modern_style
import time

# --- CONFIGURAÇÃO ---
empresa_nome, logo_src = obter_dados_empresa()
st.set_page_config(page_title=f"Painel de Controle | {empresa_nome}", layout="wide", page_icon="⚙️")
apply_modern_style(logo_url=logo_src, nome_empresa=empresa_nome)

verificar_autenticacao()
verificar_nivel_acesso(["ADMIN"])
verificar_permissao_modulo("Painel de Controle")

st.title("⚙️ Painel de Controle - Juviks Hero (v2.5)")
st.markdown("Gerenciamento crítico do sistema. **Use com cautela.**")

tab_reset, tab_ngrok, tab_manutencao, tab_logs = st.tabs(["🚀 RESET DE FÁBRICA", "🌐 NGROK / ACESSO ONLINE", "🛠️ MANUTENÇÃO", "📜 AUDITORIA"])

with tab_reset:
    st.error("### ⚠️ ZONA DE PERIGO: RESET TOTAL")
    st.markdown("""
        Esta ação irá:
        1. **Apagar TODOS os Clientes**
        2. **Apagar TODOS os Orçamentos e Históricos**
        3. **Limpar Agenda e Financeiro**
        4. **Resetar Catálogo de Produtos**
        5. **Encerrar todas as sessões ativas**
        
        *Nota: O usuário 'admin' e as configurações básicas da empresa serão mantidos.*
    """)
    
    confirm_text = st.text_input("Para prosseguir, digite **LIMPAR TUDO AGORA** abaixo:", placeholder="Digite aqui...")
    
    if st.button("🚨 EXECUTAR LIMPEZA COMPLETA DO SISTEMA", type="primary", use_container_width=True):
        if confirm_text == "LIMPAR TUDO AGORA":
            with st.spinner("Limpando banco de dados..."):
                try:
                    tables_to_clear = [
                        "clientes", "orcamentos", "agenda", "financeiro", 
                        "sessoes_ativas", "logs_acesso", "projetos", 
                        "vendedores", "formas_pagamento", "modelos_contrato", 
                        "categorias_produtos", "produtos"
                    ]
                    
                    for table in tables_to_clear:
                        executar_comando(f"DELETE FROM {table}")
                    
                    # 1. Configurar Nome Padrão
                    executar_comando("DELETE FROM config")
                    executar_comando("INSERT INTO config (empresa_nome) VALUES (?)", ("JUVICK",))
                    
                    # 2. Configurar Usuário Admin Padrão
                    n_u, n_p, n_k = "admin", "admin123", "JUV-HERO-071719"
                    executar_comando("DELETE FROM usuarios")
                    executar_comando("INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES (?, ?, ?)", (n_u, n_p, "ADMIN"))
                    
                    # Pegamos o novo ID do usuário inserido
                    res_new_u = buscar_dados("SELECT id FROM usuarios WHERE usuario = ?", (n_u,))
                    new_u_id = int(res_new_u.iloc[0]['id']) if not res_new_u.empty else 1

                    # 3. Configurar Chave de Acesso Padrão
                    executar_comando("DELETE FROM chaves_acesso")
                    executar_comando("INSERT INTO chaves_acesso (codigo, usuario, descricao, status) VALUES (?, ?, ?, ?)", (n_k, n_u, "ACESSO PADRAO JUVICK", 1))

                    # 4. Salvar Novo Acesso no Hardware (Se for local)
                    try:
                        ctx = getattr(st, "context", None)
                        hdr = getattr(ctx, "headers", {}) if ctx else {}
                        host = hdr.get("Host", "").lower() if hasattr(hdr, "get") else ""
                        if any(x in host for x in ["localhost", "127.0.0.1", "192.168.", "10.", "172."]):
                            registrar_computador(n_u, n_p, n_k)
                    except: pass

                    # Re-inicializa o banco para restaurar categorias e outros dados padrão se necessário
                    inicializar_banco()
                    
                    # 5. Injetar na Sessão para Auto-Login Imediato
                    st.session_state.usuario_nome = n_u
                    st.session_state.temp_pass = n_p
                    st.session_state.chave_usada = n_k
                    st.session_state.usuario_id = new_u_id
                    st.session_state.usuario_nivel = "ADMIN"
                    st.session_state.autenticado = True
                    st.session_state.manter_acesso = True
                    
                    # Limpa a pasta de sessões
                    sessions_dir = os.path.join(BASE_DIR, "PY", "sessions")
                    if os.path.exists(sessions_dir):
                        for f in os.listdir(sessions_dir):
                            if f.endswith(".json"):
                                try: os.remove(os.path.join(sessions_dir, f))
                                except: pass

                    st.success("✅ Sistema resetado com sucesso! Redirecionando...")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao resetar: {e}")
        else:
            st.warning("Texto de confirmação incorreto.")

with tab_ngrok:
    st.write("### 🌐 Configuração do Ngrok (Acesso Online)")
    st.info("O Ngrok permite que você acesse o sistema de qualquer lugar pela internet de forma segura.")
    
    # Busca robusta pelo ngrok.exe
    candidatos_ngrok = [
        os.path.join(BASE_DIR, "ngrok.exe"),
        os.path.join(getattr(sys, '_MEIPASS', BASE_DIR), "ngrok.exe"),
        os.path.join(BASE_DIR, "PY", "ngrok.exe"),
        os.path.join(os.path.dirname(BASE_DIR), "ngrok.exe")
    ]
    
    ngrok_exe = None
    for path in candidatos_ngrok:
        if os.path.exists(path):
            ngrok_exe = path
            break
            
    if not ngrok_exe:
        st.error(f"Arquivo `ngrok.exe` não localizado. Tentamos em: {', '.join(candidatos_ngrok)}")
    else:
        # --- SEÇÃO TOKEN ---
        st.write("#### 1. Token de Autenticação")
        st.markdown("Para o sistema funcionar online, você precisa de um token gratuito do Ngrok.")
        st.markdown("👉 [Clique aqui para obter seu token no site oficial](https://dashboard.ngrok.com/get-started/your-authtoken)")
        
        novo_token = st.text_input("Cole seu Authtoken aqui:", type="password", help="O token se parece com uma sequência longa de letras e números.")
        if st.button("💾 Salvar Authtoken no Sistema", type="primary"):
            if novo_token:
                with st.spinner("Configurando..."):
                    try:
                        # Limpa o comando se o usuário colou o comando inteiro do site
                        token_limpo = novo_token.strip().replace('ngrok config add-authtoken ', '').replace('"', '')
                        res = subprocess.run([ngrok_exe, 'config', 'add-authtoken', token_limpo], capture_output=True, text=True, timeout=10)
                        if res.returncode == 0:
                            # Salva uma cópia local para o launcher ler sem depender do ngrok.yml
                            token_file = os.path.join(DATA_DIR, "ngrok_token.txt")
                            with open(token_file, "w", encoding="utf-8") as f:
                                f.write(token_limpo)
                            st.success("✅ Authtoken configurado com sucesso! Agora você pode ligar o 'Acesso Online' no ícone da bandeja.")
                        else:
                            st.error(f"Erro do Ngrok: {res.stderr}")
                    except Exception as e:
                        st.error(f"Falha ao executar ngrok.exe: {e}")
            else:
                st.warning("Por favor, insira o token antes de clicar em salvar.")

        st.write("---")
        
        # --- SEÇÃO DOMÍNIO ---
        st.write("#### 2. Domínio Personalizado (Opcional)")
        st.write("Se você reservou um domínio no Ngrok (ex: `sua-empresa.ngrok-free.app`), insira-o aqui para que o link nunca mude.")
        
        dom_file = os.path.join(DATA_DIR, "ngrok_dominio.txt")
        dom_atual = ""
        if os.path.exists(dom_file):
            try:
                with open(dom_file, "r") as f:
                    dom_atual = f.read().strip()
            except: pass
        
        novo_dom = st.text_input("Seu Domínio Ngrok:", value=dom_atual, placeholder="ex: empresa-juvix.ngrok-free.app")
        if st.button("💾 Salvar Domínio"):
            try:
                with open(dom_file, "w") as f:
                    f.write(novo_dom.strip())
                st.success("✅ Domínio salvo! Para aplicar, desligue e ligue o Acesso Online novamente.")
            except Exception as e:
                st.error(f"Erro ao salvar arquivo: {e}")

        st.write("---")
        
        # --- STATUS ---
        st.write("#### 3. Status em Tempo Real")
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=1)
            if resp.status_code == 200:
                tunnels = resp.json().get('tunnels', [])
                if tunnels:
                    st.success("🟢 O Túnel está ATIVO!")
                    for t in tunnels:
                        st.info(f"🔗 **Link de Acesso:** {t['public_url']}")
                else:
                    st.warning("🟡 Ngrok está aberto, mas não há túneis ativos.")
            else:
                st.info("⚪ Ngrok não está rodando no momento.")
        except:
            st.info("⚪ Ngrok não está rodando no momento. (Ligue-o pelo ícone na barra de tarefas)")

with tab_manutencao:
    verificar_permissao_modulo("Painel - Manutenção")
    st.write("### 🛠️ Gestão de Componentes")
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.write("#### Cache do Navegador")
            st.write("Força a limpeza do cache local (JS) e Cookies no navegador do usuário.")
            if st.button("Limpar Cache Local"):
                st.markdown("""
                    <script>
                        window.localStorage.clear();
                        document.cookie.split(";").forEach(function(c) { 
                            document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
                        });
                        window.location.reload();
                    </script>
                """, unsafe_allow_html=True)
                st.success("Comando enviado ao navegador.")

    with c2:
        with st.container(border=True):
            st.write("#### Re-indexar Banco de Dados")
            st.write("Executa o VACUUM no SQLite para reduzir tamanho e melhorar performance.")
            if st.button("Otimizar Banco"):
                try:
                    executar_comando("VACUUM")
                    st.success("Otimização concluída!")
                except Exception as e:
                    st.error(e)

    st.write("---")
    st.write("### 🔑 Credenciais do Administrador (Admin)")
    st.write("Altere a senha e a chave de acesso do usuário principal `admin`.")
    with st.form("form_change_admin"):
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            nova_senha_admin = st.text_input("Nova Senha do Admin", type="password")
        with c_a2:
            nova_chave_admin = st.text_input("Nova Chave do Admin", placeholder="Ex: CHAVE-ADMIN-123")
        
        if st.form_submit_button("Atualizar Credenciais", type="primary", use_container_width=True):
            if nova_senha_admin and nova_chave_admin:
                try:
                    # 1. Atualizar a senha do usuário 'admin'
                    executar_comando("UPDATE usuarios SET senha=? WHERE LOWER(usuario)='admin'", (nova_senha_admin,))
                    
                    # 2. Atualizar ou inserir a chave de acesso do 'admin'
                    res_chave = buscar_dados("SELECT id FROM chaves_acesso WHERE LOWER(usuario)='admin'")
                    if not res_chave.empty:
                        executar_comando("UPDATE chaves_acesso SET codigo=? WHERE LOWER(usuario)='admin'", (nova_chave_admin.strip().upper(),))
                    else:
                        executar_comando("INSERT INTO chaves_acesso (codigo, usuario, descricao, status) VALUES (?, 'admin', 'ACESSO PADRAO ADMIN', 1)", (nova_chave_admin.strip().upper(),))
                    
                    # 3. Atualizar hardware_license se aplicável (opcional, mas bom manter coerência)
                    try:
                        ctx = getattr(st, "context", None)
                        hdr = getattr(ctx, "headers", {}) if ctx else {}
                        host = hdr.get("Host", "").lower() if hasattr(hdr, "get") else ""
                        if any(x in host for x in ["localhost", "127.0.0.1", "192.168.", "10.", "172."]):
                            registrar_computador("admin", nova_senha_admin, nova_chave_admin.strip().upper())
                    except: pass
                    
                    st.success("✅ Senha e Chave do Admin atualizadas com sucesso! Por segurança, saia e faça login novamente com as novas credenciais.")
                except Exception as e:
                    st.error(f"Erro ao atualizar credenciais: {e}")
            else:
                st.warning("Preencha a nova senha e a nova chave para atualizar.")

    st.write("---")
    st.write("### 📂 Gerenciamento de Arquivos (Modo Executável)")
    st.write(f"**Diretório Base:** `{BASE_DIR}`")
    st.write(f"**Caminho do Banco:** `{DB_PATH}`")
    
    if st.button("Verificar Pastas Essenciais"):
        dirs = ["DATABASE", "LICENSA", "PY/sessions", "BAT", "SUGESTOES"]
        for d in dirs:
            p = os.path.join(BASE_DIR, d)
            if os.path.exists(p):
                st.write(f"✅ `{d}` - Localizado")
            else:
                st.write(f"❌ `{d}` - Não encontrado")

with tab_logs:
    verificar_permissao_modulo("Painel - Auditoria")
    st.write("### 📜 Logs Recentes de Acesso")
    df_logs = buscar_dados("SELECT * FROM logs_acesso ORDER BY id DESC LIMIT 100")
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("Nenhum log encontrado.")
    
    if st.button("Exportar Logs (CSV)"):
        if not df_logs.empty:
            csv = df_logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Baixar CSV",
                csv,
                "logs_sistema.csv",
                "text/csv",
                key='download-csv'
            )


