# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys
import time
import requests
from PIL import Image
from utils.auth_manager import verificar_autenticacao, verificar_permissao_modulo, obter_dados_empresa

# Adicionar pasta raiz ao path se necessário
if getattr(sys, 'frozen', False):
    sys.path.append(sys._MEIPASS)
else:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TEMAS.moderno import apply_modern_style

empresa_nome, logo_src = obter_dados_empresa()
st.set_page_config(page_title=f"Conexão WhatsApp | {empresa_nome}", layout="wide", page_icon="📲")
apply_modern_style(logo_url=logo_src, nome_empresa=empresa_nome)

# Validação do Login e Acesso
verificar_autenticacao()
if not verificar_permissao_modulo("Config - Motor WhatsApp"):
    st.warning("🚫 Você não tem permissão para acessar o Gerenciador de Envio.")
    st.stop()

# Estilo Premium
st.markdown("""
    <style>
    .status-card {
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📲 Gerenciador de Envio (API)")
st.markdown("Conecte o seu WhatsApp principal para automatizar o envio de orçamentos e contratos.")

# URL do Coração do Zap (Motor Local - Alinhado com gateway.js)
GATEWAY_URL = "http://127.0.0.1:3000"

def get_status():
    try:
        resp = requests.get(f"{GATEWAY_URL}/status", timeout=2)
        return resp.json()
    except:
        return {"status": "offline"}

# --- Lógica principal ---
status_data = get_status()
current_status = status_data.get('status', 'offline')

c1, c2 = st.columns([1, 1])

with c1:
    st.markdown("### 📡 Status da Instância")
    if current_status == "ready":
        st.success("✅ CONECTADO E PRONTO")
        st.info(f"Conectado como: {status_data.get('user', 'Desconhecido')}")
        if st.button("🚫 Desconectar / Trocar Conta", type="primary", use_container_width=True):
            try: requests.get(f"{GATEWAY_URL}/logout")
            except: pass
            st.rerun()
    elif current_status == "loading":
        st.warning("⏳ INICIALIZANDO...")
        st.info("O robô está acordando, aguarde uns segundos.")
    elif current_status == "qr":
        st.info("📷 AGUARDANDO SCAN")
        st.markdown("Abra o WhatsApp no seu celular > Configurações > Dispositivos Conectados > Conectar um dispositivo.")
    else:
        st.error("❌ SISTEMA OFFLINE")
        st.markdown("O motor de envio não está rodando.")

    st.write("---")
    
    # Botões de Ação
    if st.button("🚀 LIGAR MOTOR DE ENVIO", type="primary", use_container_width=True):
        import subprocess
        motor_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "WHATSAPP_MOTOR")
        # Comando invisível para o Windows
        CREATE_NO_WINDOW = 0x08000000
        try:
            subprocess.Popen(["node", "gateway.js"], cwd=motor_dir, creationflags=CREATE_NO_WINDOW)
            st.info("Iniciando motor em background... Aguarde 10s.")
            time.sleep(5)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao ligar: {e}")

    if st.button("🗑️ LIMPAR REGISTRO E CACHE", use_container_width=True, help="Apaga TUDO (Sessão e Cache) para resolver travamentos"):
        import shutil
        motor_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "WHATSAPP_MOTOR")
        
        # Pastas de limpeza
        auth_dir = os.path.join(motor_dir, ".wwebjs_auth")
        cache_dir = os.path.join(motor_dir, ".wwebjs_cache")
        qr_file = os.path.join(motor_dir, "qr.png")
        
        # 1. Mata qualquer processo node pendente
        os.system("taskkill /F /IM node.exe")
        time.sleep(1)
        
        # 2. Apaga as pastas de dados
        try:
            if os.path.exists(auth_dir): shutil.rmtree(auth_dir)
            if os.path.exists(cache_dir): shutil.rmtree(cache_dir)
            if os.path.exists(qr_file): os.remove(qr_file)
            st.success("🔥 SESSÃO E CACHE LIMPOS COM SUCESSO!")
        except Exception as e:
            st.warning(f"Alguns arquivos não puderam ser limpos (podem estar em uso): {e}")
            
        st.info("Agora clique em 'LIGAR MOTOR' para iniciar do zero.")
        st.rerun()

with c2:
    if current_status == "qr":
        qr_string = status_data.get('qr')
        if qr_string and qr_string.startswith('data:image'):
            import base64
            # Pega apenas a parte base64 da string
            b64_data = qr_string.split(',')[1]
            image_bytes = base64.b64decode(b64_data)
            st.image(image_bytes, caption="ESCANEIE PARA CONECTAR", width=320)
        elif qr_string:
            # Caso seja o fallback para string e o qrcode não exista
            st.info("🔄 Preparando visualização... Aguarde.")
        else:
            st.info("🔄 Gerando código no WhatsApp... Aguarde.")
    elif current_status == "ready":
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.markdown("### 🎉 Tudo Certo!")
        st.markdown("Seu WhatsApp já está integrado e pronto para os envios automáticos.")
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown("### 📝 Personalização da Mensagem de Envio")
st.markdown("Defina o texto que acompanhará o PDF do orçamento.")

# Busca configuração atual
from database import buscar_dados, executar_comando
df_config = buscar_dados("SELECT wpp_msg_orcamento FROM config LIMIT 1")
msg_atual = df_config.iloc[0]['wpp_msg_orcamento'] if not df_config.empty and df_config.iloc[0]['wpp_msg_orcamento'] else "Olá {{cliente_nome}}! Segue o seu orçamento conforme solicitado. (Ref: {{numero_orcamento}})"

with st.container(border=True):
    nova_msg = st.text_area("Modelo da Mensagem", value=msg_atual, height=120, help="Use as tags do guia abaixo para preenchimento automático.")
    
    if st.button("💾 Salvar Modelo de Mensagem", use_container_width=True, type="secondary"):
        try:
            executar_comando("UPDATE config SET wpp_msg_orcamento = ?", (nova_msg,))
            st.success("Modelo de mensagem salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    # --- GUIA DE TAGS AVANÇADO (Sempre Visível) ---
    st.markdown("---")
    st.markdown("### 📌 Guia de Tags Disponíveis")
    st.markdown("""
        Copie e cole as tags abaixo no seu texto para preenchimento automático:
        - `{{numero_orcamento}}` : Código do orçamento (Ex: ORC-202401)
        - `{{cliente_nome}}` : Nome completo do cliente
        - `{{valor_total}}` : Valor total formatado (R$)
        - `{{vendedor}}`    : Nome do consultor responsável
        - `{{data}}`        : Data de geração
        - `{{empresa}}`     : Nome da sua empresa
    """)
    st.info("💡 Exemplo: *Olá {{cliente_nome}}, seu orçamento {{numero_orcamento}} no valor de {{valor_total}} está pronto!*")

st.divider()
st.markdown("⚠️ **Importante:** Este sistema usa uma API segura e privada que roda apenas no seu computador.")

# Auto-refresh inteligente no final (apenas se não estiver pronto)
if current_status in ["qr", "loading", "offline"]:
    if "last_refresh" not in st.session_state or time.time() - st.session_state["last_refresh"] > 4:
        st.session_state["last_refresh"] = time.time()
        time.sleep(4)
        st.rerun()
