import streamlit as st
import os
import hashlib
import subprocess

import sys
from functools import lru_cache
# --- LOCALIZAÇÃO ROBUSTA DA LICENÇA ---
def get_safe_license_dir():
    try:
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
            if "Program Files" in app_dir or "Arquivos de Programas" in app_dir:
                appdata_juvicks = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "JUVICKS_DATA")
                if not os.path.exists(appdata_juvicks): os.makedirs(appdata_juvicks, exist_ok=True)
                return os.path.join(appdata_juvicks, "LICENSA")
            return os.path.join(app_dir, "LICENSA")
        else:
            _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(_root, "LICENSA")
    except:
        return os.path.join(os.getcwd(), "LICENSA")

LICENSE_DIR = get_safe_license_dir()
LICENSE_FILE = os.path.join(LICENSE_DIR, "license.key")

# 🔑 ESTA É A SUA CHAVE MESTRA (Não mude depois de começar a vender)
# Ela garante que as licenças geradas pelo SEU gerador funcionem no SEU sistema.
MASTER_SECRET = "JUVIKS_2026_HERO_SECURE_VAULT"

@lru_cache(maxsize=1)
def get_hwid():
    """Gera um ID único baseado no hardware (Placa-Mãe -> Disco -> MAC)."""
    serial = ""
    try:
        # 1. Tenta Placa-Mãe
        cmd_mb = "wmic baseboard get serialnumber"
        output = subprocess.check_output(cmd_mb, shell=True).decode().split('\n')
        if len(output) > 1: serial = output[1].strip()
        
        # 2. Se falhar, tenta Disco Rígido
        if not serial or "To be filled" in serial or "None" in serial:
            cmd_disk = "wmic diskdrive get serialnumber"
            output_d = subprocess.check_output(cmd_disk, shell=True).decode().split('\n')
            if len(output_d) > 1: serial = output_d[1].strip()
            
        # 3. Se tudo falhar, usa o MAC Address (UUID) como garantia
        if not serial or "None" in serial:
            import uuid
            serial = str(uuid.getnode())

        # Cria um hash de 12 caracteres: XXXX-XXXX-XXXX
        raw_hwid = hashlib.sha256(serial.encode()).hexdigest().upper()[:12]
        return f"{raw_hwid[:4]}-{raw_hwid[4:8]}-{raw_hwid[8:]}"
    except:
        # Fallback de emergência absoluto (MAC Address puro)
        import uuid
        node = str(uuid.getnode())
        raw_hwid = hashlib.sha256(node.encode()).hexdigest().upper()[:12]
        return f"{raw_hwid[:4]}-{raw_hwid[4:8]}-{raw_hwid[8:]}"

def gerar_chave_final(hwid):
    """Gera a Licença Final baseada no HWID fornecido."""
    # Combina o HWID do cliente com o seu Segredo Mestre
    raw_key = hashlib.sha256(f"{hwid}{MASTER_SECRET}".encode()).hexdigest().upper()[:16]
    # Formata como XXXX-XXXX-XXXX-XXXX
    return f"{raw_key[:4]}-{raw_key[4:8]}-{raw_key[8:12]}-{raw_key[12:]}"

def salvar_licenca(key):
    if not os.path.exists(LICENSE_DIR):
        os.makedirs(LICENSE_DIR)
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(key.strip())

def ler_licenca():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except:
            return None
    return None

def verificar_licenca():
    """Verifica se a licença no arquivo bate com o Hardware atual ou se é uma licença SaaS válida."""
    # Fast path: Se já validado na sessão atual, não repete consultas pesadas ao DB/Hardware
    if st.session_state.get("licenca_valida"):
        return True

    chave_armazenada = ler_licenca()
    hwid_maquina = get_hwid()
    chave_esperada = gerar_chave_final(hwid_maquina)
    
    # 1. Chave de Emergência (Universal)
    CHAVE_MESTRA = "JUV-2026-HERO-PRO-99" 
    
    if chave_armazenada == chave_esperada or chave_armazenada == CHAVE_MESTRA:
        st.session_state.licenca_valida = True
        return True
    
    exibir_tela_bloqueio()
    st.stop()

def start_activation_server():
    import threading
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
        def do_POST(self):
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                key = data.get('key', '').strip().upper()
                if key:
                    salvar_licenca(key)
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                
    def run_server():
        try:
            httpd = HTTPServer(('localhost', 8599), Handler)
            httpd.serve_forever()
        except:
            pass # Ignora se a porta ja estiver em uso
            
    # Inicia apenas se ainda nao estiver rodando na sessao
    if "activation_server_started" not in st.session_state:
        st.session_state.activation_server_started = True
        t = threading.Thread(target=run_server, daemon=True)
        t.start()

def exibir_tela_bloqueio():
    """Interface de bloqueio 100% IDENTICA ao modelo HTML original do cliente."""
    start_activation_server()
    hwid = get_hwid()

    # 1. Verifica se a interface HTML enviou a chave de volta via URL Array
    if 'act_key' in st.query_params:
        key_input = st.query_params.get("act_key").strip().upper()
        chave_correta = gerar_chave_final(hwid)
        if key_input == chave_correta or key_input == "JUV-2026-HERO-PRO-99" or key_input == "JUV2026HEROPRO99":
            salvar_licenca(key_input)
            st.query_params.clear()
            st.session_state.licenca_valida = True
            st.rerun()

    # 2. Oculta todo o framework Streamlit para dar lugar ao HTML Fullscreen
    st.markdown("""
        <style>
        [data-testid="stSidebar"], [data-testid="stHeader"], footer {display: none !important;}
        .block-container {padding: 0 !important; max-width: 100% !important; margin: 0 !important;}
        body, .stApp {background-color: #07080d !important;}
        iframe {border: none; width: 100vw; height: 100vh;}
        </style>
    """, unsafe_allow_html=True)

    # --- LOCALIZAÇÃO ROBUSTA DO TEMPLATE ---
    tentativas = []
    html_path = None
    
    if getattr(sys, 'frozen', False):
        # 1. Tenta no bundle interno (_MEIPASS)
        base_meipass = getattr(sys, '_MEIPASS', '')
        if base_meipass:
            path_mei = os.path.join(base_meipass, "TELA", "juviks_activation.html")
            tentativas.append(path_mei)
            if os.path.exists(path_mei): html_path = path_mei
        
        # 2. Tenta na pasta do EXE (Instalação no C:)
        if not html_path:
            exe_dir = os.path.dirname(sys.executable)
            path_exe = os.path.join(exe_dir, "TELA", "juviks_activation.html")
            tentativas.append(path_exe)
            if os.path.exists(path_exe): html_path = path_exe
    else:
        # Modo Desenvolvimento
        _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path_dev = os.path.join(_root, "TELA", "juviks_activation.html")
        tentativas.append(path_dev)
        if os.path.exists(path_dev): html_path = path_dev

    # 3. Fallback final: Pasta de trabalho atual
    if not html_path:
        path_cwd = os.path.join(os.getcwd(), "TELA", "juviks_activation.html")
        tentativas.append(path_cwd)
        if os.path.exists(path_cwd): html_path = path_cwd

    if html_path:
        try:
            from database import ler_arquivo_seguro
            html = ler_arquivo_seguro(html_path)
        except Exception:
            with open(html_path, "r", encoding="utf-8", errors="replace") as f:
                html = f.read()
            
        chave_correta = gerar_chave_final(hwid)
        
        # Injeta HWID Dinâmico
        html = html.replace("D11B-4863-A1D5", hwid)
        
        # Injeta Lógica de Validação Customizada do Cliente
        html = html.replace("const valid = key.startsWith('JVK');", 
                            f"const valid = (key === '{chave_correta}' || key === 'JUV-2026-HERO-PRO-99' || key === 'JUV2026HEROPRO99');")

        # Injeta bridge de comunicação do Javascript pro Backend Python
        old_sucesso = "showMessage('success', '✓ Licença ativada com sucesso! Reiniciando o sistema...');"
        new_sucesso = old_sucesso + """
        fetch('http://localhost:8599', { method: 'POST', body: JSON.stringify({ key: key }) });
        setTimeout(() => { alert('A Chave foi aplicada com sucesso! Por favor feche esta aba e o seu Painel de Controle e abra o sistema novamente para recarregar!'); }, 1800);
        """
        html = html.replace(old_sucesso, new_sucesso)

        import streamlit.components.v1 as components
        components.html(html, height=1000, scrolling=False)
    else:
        st.error(f"⚠️ Template de Ativação não encontrado!")
        st.info(f"Caminhos verificados: \n- " + "\n- ".join(tentativas))
        st.warning("Certifique-se de que a pasta 'TELA' foi incluída na instalação ou na raiz do projeto.")
