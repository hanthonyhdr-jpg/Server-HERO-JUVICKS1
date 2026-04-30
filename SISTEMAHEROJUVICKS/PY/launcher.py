# -*- coding: utf-8 -*-
import os
import sys
import pystray
from PIL import Image
import subprocess
import socket
import webbrowser
import requests
import threading
import time
import sqlite3
import io
import base64
import multiprocessing
import ctypes
import shutil

# --- UTILITÁRIO DE CAMINHOS UNIFICADO ---
def get_resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, compatível com PyInstaller 6+ """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        # No PyInstaller 6+, arquivos de dados costumam ficar em _internal no modo OneDir
        internal_path = os.path.join(base_path, "_internal")
        
        # Tenta primeiro na raiz do _MEIPASS, depois em _internal
        p1 = os.path.join(base_path, relative_path)
        if os.path.exists(p1): return os.path.normpath(p1)
        
        p2 = os.path.join(internal_path, relative_path)
        return os.path.normpath(p2)
    else:
        # Se for script, usa a raiz do projeto (pai de /PY)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.normpath(os.path.join(base_path, relative_path))

def get_data_path(relative_path):
    """ Retorna o caminho para dados persistentes (LOCALAPPDATA) """
    data_root = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "JUVICKS_DATA")
    
    # Se estivermos rodando de uma pasta protegida (Program Files), usamos obrigatoriamente LOCALAPPDATA
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        if any(x in exe_dir for x in ["Program Files", "Arquivos de Programas"]):
             os.makedirs(data_root, exist_ok=True)
             return os.path.normpath(os.path.join(data_root, relative_path))
    
    # Caso contrário, usa a raiz do projeto para facilitar portabilidade em pastas não protegidas
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base_path, relative_path))

# Variáveis globais de controle
ngrok_process = None
ngrok_ativo = False
streamlit_process = None
flask_proc = None
whatsapp_process = None

# Função para verificar se a porta está em uso
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_flask():
    """Inicia o servidor Flask das assinaturas na porta 5001"""
    global flask_proc
    if flask_proc is None:
        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, "flask", "--port", "5001"]
            flask_proc = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            flask_app = get_resource_path(os.path.join("PY", "assiname_app", "app.py"))
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            flask_proc = subprocess.Popen([python_exe, flask_app, "--port", "5001"], 
                                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

def stop_flask():
    global flask_proc
    if flask_proc:
        flask_proc.terminate()
        flask_proc = None

# 1. IP da rede local
def get_network_url():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:8501"
    except Exception:
        return "URL não disponível"

# 2. Captura link público do Ngrok via API local
def get_ngrok_url(port=8501):
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=0.5)
        if response.status_code == 200:
            for t in response.json().get('tunnels', []):
                addr = t.get('config', {}).get('addr', '')
                if f":{port}" in addr or addr.endswith(str(port)):
                    return t.get('public_url')
    except: pass
    return None

# 4. Iniciar Streamlit (Compatível com EXE e Script)
def start_streamlit():
    global streamlit_process
    
    # --- MELHORIA: Limpeza forçada da porta antes de iniciar ---
    try:
        # Mata qualquer processo que esteja ocupando a porta 8501 para evitar o erro 404
        kill_cmd = 'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :8501 ^| findstr LISTENING\') do taskkill /F /PID %a'
        subprocess.run(f'cmd /c "{kill_cmd}"', shell=True, capture_output=True)
        time.sleep(1)
    except:
        pass

    if not is_port_in_use(8501):
        if getattr(sys, 'frozen', False):
            # No modo EXE (PyInstaller), a base é sys._MEIPASS
            base_dir = sys._MEIPASS
            python_exe = sys.executable
            app_py = "Inicio.py" 
            
            # Quando congelado, chamamos o próprio EXE com os argumentos do streamlit
            cmd = [python_exe, "streamlit", "run", app_py,
                   "--server.address", "0.0.0.0", 
                   "--server.port", "8501",
                   "--global.developmentMode", "false",
                   "--browser.gatherUsageStats", "false",
                   "--server.headless", "true"]
            
            # CWD É A PASTA PY (crucial para o erro de não abrir pós compilação)
            # No PyInstaller 6+, ela costuma ficar em _internal
            launch_cwd = os.path.join(base_dir, "PY")
            if not os.path.exists(os.path.join(launch_cwd, app_py)):
                launch_cwd = os.path.join(base_dir, "_internal", "PY")
        else:
            # No modo script (desenvolvimento)
            base_dir = os.path.dirname(os.path.abspath(__file__)) # /PY
            python_exe = sys.executable
            app_py = "Inicio.py"
            cmd = [python_exe, "-m", "streamlit", "run", app_py,
                   "--server.address", "0.0.0.0", 
                   "--server.port", "8501",
                   "--global.developmentMode", "false",
                   "--browser.gatherUsageStats", "false",
                   "--server.headless", "true"]
            launch_cwd = base_dir # Executa de dentro da /PY

        # Inicia o processo e guarda o handle
        streamlit_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW, cwd=launch_cwd)

def _desligar_streamlit():
    global streamlit_process
    try:
        # Tenta encerrar o handle guardado
        if streamlit_process:
            streamlit_process.terminate()
            streamlit_process = None
        
        # --- OPCAO NUCLEAR: PROCURA E MATA QUEM ESTIVER NA PORTA 8501 ---
        # Isso garante que o motor do sistema morra mesmo se o handle falhar
        kill_cmd = 'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :8501 ^| findstr LISTENING\') do taskkill /F /PID %a'
        subprocess.run(f'cmd /c "{kill_cmd}"', shell=True, capture_output=True)

        # Mata qualquer Streamlit ou Python residual deste projeto
        if getattr(sys, 'frozen', False):
            my_name = os.path.basename(sys.executable)
            subprocess.run(['taskkill', '/F', '/IM', my_name, '/T'], capture_output=True)
        else:
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq streamlit*', '/T'], capture_output=True)
    except:
        pass

# 4. LIGAR Ngrok em thread separada
def _ligar_ngrok(port=None):
    """
    Liga o Ngrok. Se port for None, tenta ligar ambos (8501 e 5001) usando um config file temporario
    para contornar limites de 1 sessao por conta free.
    """
    global ngrok_process, ngrok_proc_pdf, ngrok_ativo
    try:
        ngrok_exe = get_resource_path("ngrok.exe")
        project_dir = os.path.dirname(ngrok_exe)
            
        if not os.path.exists(ngrok_exe): return

        # Pegar token
        token = ""
        # 1. Tentar ler do nosso arquivo local (Mais confiavel)
        token_local_file = get_data_path("ngrok_token.txt")
        if os.path.exists(token_local_file):
            try:
                with open(token_local_file, 'r', encoding="utf-8") as f:
                    token = f.read().strip()
            except: pass
            
        # 2. Se nao achou, tenta o padrao do Ngrok
        if not token:
            import platform
            if platform.system() == 'Windows':
                cfg_path_real = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ngrok', 'ngrok.yml')
            else:
                cfg_path_real = os.path.expanduser('~/.config/ngrok/ngrok.yml')
            
            if os.path.exists(cfg_path_real):
                with open(cfg_path_real, 'r', encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if 'authtoken:' in line and not line.strip().startswith('#'):
                            # Caso 1: Token na mesma linha
                            parts = line.split('authtoken:')
                            val = parts[-1].strip().strip('"').strip("'")
                            if val and val not in ['|-', '|']:
                                token = val
                                break
                            # Caso 2: Token na linha seguinte (formato YAML block)
                            elif i + 1 < len(lines):
                                next_line = lines[i+1].strip().strip('"').strip("'")
                                if len(next_line) > 20:
                                    token = next_line
                                    break

        # Criar config ad-hoc para múltiplos túneis em local gravável (crucial para Program Files)
        tmp_cfg = get_data_path("ngrok_temp.yml")
        
        # Garante que a pasta pai do tmp_cfg existe
        os.makedirs(os.path.dirname(tmp_cfg), exist_ok=True)
        
        with open(tmp_cfg, "w", encoding="utf-8") as f:
            f.write(f"authtoken: {token}\n")
            f.write("version: '2'\n")
            f.write("tunnels:\n")
            f.write("  painel:\n    proto: http\n    addr: 8501\n")
            
            # Dominio painel (lido de local gravável)
            dom_panel = get_data_path("ngrok_dominio.txt")
            if os.path.exists(dom_panel):
                with open(dom_panel, "r", encoding="utf-8") as df:
                    d = df.read().strip()
                    if d: f.write(f"    domain: {d}\n")

        cmd = [ngrok_exe, 'start', '--all', '--config', tmp_cfg]
        ngrok_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Pequeno delay para verificar se o processo não morreu imediatamente
        time.sleep(1.5)
        if ngrok_process.poll() is None:
            ngrok_ativo = True
        else:
            # Se o processo morreu, tenta capturar o erro (opcional, difícil sem console)
            ngrok_ativo = False
    except Exception as e:
        # Log do erro para ajudar o suporte
        try:
            err_log = get_data_path("ERRO_NGROK.txt")
            with open(err_log, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] Falha ao ligar Ngrok: {str(e)}\n")
        except: pass
        ngrok_ativo = False

def _desligar_ngrok(port=None):
    global ngrok_process, ngrok_ativo
    try:
        if ngrok_process:
            ngrok_process.terminate()
            ngrok_process = None
        subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe', '/T'], capture_output=True, timeout=5)
    except: pass
    ngrok_ativo = False

def _tem_token_ngrok(ngrok_exe):
    """Verifica se ja existe um authtoken configurado para este usuario."""
    # 1. Verifica no nosso arquivo local
    token_local_file = get_data_path("ngrok_token.txt")
    if os.path.exists(token_local_file):
        try:
            with open(token_local_file, 'r', encoding="utf-8") as f:
                if len(f.read().strip()) > 15: return True
        except: pass

    try:
        # 2. Verifica no ngrok config check
        result = subprocess.run(
            [ngrok_exe, 'config', 'check'],
            capture_output=True, text=True, timeout=5
        )
        cfg_output = result.stdout + result.stderr
        if 'authtoken' in cfg_output.lower():
            return True
            
        # 3. Verifica manualmente nos locais padrao
        import platform
        paths = []
        if platform.system() == 'Windows':
            paths.append(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ngrok', 'ngrok.yml'))
            paths.append(os.path.join(os.path.expanduser('~'), '.ngrok2', 'ngrok.yml'))
        else:
            paths.append(os.path.expanduser('~/.config/ngrok/ngrok.yml'))
            paths.append(os.path.expanduser('~/.ngrok2/ngrok.yml'))

        for cfg_path in paths:
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if 'authtoken:' in content:
                    token_line = [l for l in content.splitlines() if 'authtoken:' in l and not l.strip().startswith('#')]
                    if token_line:
                        token_val = token_line[0].split('authtoken:')[-1].strip().strip('"')
                        if len(token_val) > 15:
                            return True
    except: pass
    return False

def _pedir_token_ngrok(ngrok_exe):
    """Abre janela grafica pedindo o token Ngrok ao usuario."""
    try:
        import tkinter as tk
        from tkinter import simpledialog, messagebox
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        messagebox.showinfo(
            "🌐 Configurar Acesso Online",
            "Para usar o Acesso Online, você precisa de uma conta gratuita no Ngrok.\n\n"
            "1. Acesse: https://dashboard.ngrok.com/\n"
            "2. Crie sua conta gratuita\n"
            "3. Copie seu Token em 'Your Authtoken'\n"
            "4. Cole o token na próxima tela",
            parent=root
        )
        
        token = simpledialog.askstring(
            "Token Ngrok",
            "Cole aqui o seu Authtoken do Ngrok:",
            parent=root
        )
        root.destroy()
        
        if token:
            # Limpeza robusta: remove o comando se o usuário colou o comando inteiro
            token = token.strip()
            token = token.replace('ngrok.exe config add-authtoken ', '')
            token = token.replace('ngrok config add-authtoken ', '')
            token = token.replace('ngrok.exe authtoken ', '')
            token = token.replace('ngrok authtoken ', '')
            token = token.replace('"', '').replace("'", "")
            
            if len(token) > 20:
                # 1. Salva no Ngrok Global
                subprocess.run(
                    [ngrok_exe, 'config', 'add-authtoken', token],
                    capture_output=True, timeout=10
                )
                # 2. Salva localmente para persistência garantida do sistema
                token_local_file = get_data_path("ngrok_token.txt")
                try:
                    with open(token_local_file, 'w', encoding="utf-8") as f:
                        f.write(token)
                except: pass
                return True
    except Exception as e:
        pass
    return False

# 6. Toggle Ngrok chamado pelo menu
def toggle_ngrok(icon, item):
    def run_toggle():
        url = get_ngrok_url(8501)
        if url:
            _desligar_ngrok()
        else:
            ngrok_local = get_resource_path("ngrok.exe")
            
            if not _tem_token_ngrok(ngrok_local):
                if not _pedir_token_ngrok(ngrok_local): return
            
            _ligar_ngrok()
        icon.update_menu()
        
    threading.Thread(target=run_toggle, daemon=True).start()


def _ligar_whatsapp():
    """Lança o motor do WhatsApp em segundo plano (Obrigatório porta 8080)"""
    global whatsapp_process
    try:
        motor_dir = get_resource_path(os.path.join("PY", "WHATSAPP_MOTOR"))
        gateway_js = os.path.join(motor_dir, "gateway.js")
        if os.path.exists(gateway_js):
            # Log de saída para debug do motor
            log_path = get_data_path(os.path.join("DATABASE", "motor_zap.log"))
            log_file = open(log_path, "a", encoding="utf-8")
            
            # Checagem de portabilidade: Usa o Node embutido se existir, senão usa o do sistema
            node_exe = os.path.join(motor_dir, "node.exe")
            if not os.path.exists(node_exe):
                node_exe = 'node'
                
            cmd = [node_exe, gateway_js]
            whatsapp_process = subprocess.Popen(cmd, cwd=motor_dir, stdout=log_file, stderr=log_file, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception: pass

def stop_all(icon=None, item=None):
    global ngrok_process, streamlit_process, flask_proc, whatsapp_process
    print("[+] Encerrando todos os processos...")
    
    # 1. Desliga Ngrok
    _desligar_ngrok()
    
    # 2. Desliga Streamlit (com limpeza de porta)
    _desligar_streamlit()
    
    # 3. Desliga Flask
    stop_flask()
    
    # 4. Desliga WhatsApp (Node)
    if whatsapp_process:
        try:
            whatsapp_process.terminate()
        except: pass
        whatsapp_process = None
        
    # 5. Limpeza nuclear de processos órfãos
    try:
        # Mata qualquer processo node residual
        subprocess.run(['taskkill', '/F', '/IM', 'node.exe', '/T'], capture_output=True)
        # Mata qualquer processo python que possa ter ficado preso
        if not getattr(sys, 'frozen', False):
             subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq streamlit*', '/T'], capture_output=True)
    except: pass
    
    if icon:
        icon.stop()
        os._exit(0)

def _abrir_em_modo_app(url):
    """Tenta abrir a URL em modo 'app' (sem barra de endereço/abas) no Chrome ou Edge."""
    browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for path in browsers:
        if os.path.exists(path):
            try:
                subprocess.Popen([path, f"--app={url}"])
                return True
            except: pass
    webbrowser.open(url)
    return False

def abrir_navegador_local(icon=None, item=None):
    _abrir_em_modo_app('http://localhost:8501')

def abrir_navegador_internet(icon=None, item=None):
    url = get_ngrok_url()
    if url:
        _abrir_em_modo_app(url)

def reiniciar_sistema(icon, item):
    """Executa a Parada Total (2) e o Início (1) em um clique."""
    try:
        # Passo 1: Parar tudo (Função 2 do BAT)
        stop_all()
        icon.stop()
        
        # Passo 2: Iniciar tudo novamente (Função 1 do BAT)
        python_exe = sys.executable
        launcher_script = sys.argv[0]
        
        # Lança um novo processo independente
        subprocess.Popen([python_exe, launcher_script], creationflags=subprocess.CREATE_NEW_CONSOLE if not getattr(sys, 'frozen', False) else 0)
        
        # Encerra o processo atual
        os._exit(0)
    except:
        os._exit(1)

def create_image():
    # ─── LOGICA DE ICONE DINAMICO ───
    # 1. Tentar pegar o Logo Oficial do Banco de Dados (Configurado pelo Usuario)
    try:
        db_path = get_data_path(os.path.join("DATABASE", "sistema_vendas.db"))
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT logo_data FROM config LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                logo_bytes = base64.b64decode(row[0])
                return Image.open(io.BytesIO(logo_bytes))
    except:
        pass

    # 2. Se nao tiver no banco, procurar nas pastas de Icone externas
    base_dir = get_resource_path("") # _MEIPASS no EXE
    external_dir = os.path.dirname(get_data_path("dummy")) # Raiz ou LOCALAPPDATA

    try:
        paths = [
            get_data_path(os.path.join("ICONE", "ICONE.ico")),
            get_resource_path(os.path.join("ICONE", "ICONE.ico")),
            os.path.join(base_dir, "ICONE", "ICONE.ico"),
            os.path.join(external_dir, "ICONE", "ICONE.ico")
        ]
        
        for p in paths:
            if os.path.exists(p):
                return Image.open(p)
    except:
        pass

    # 3. Fallback Final (Bloco Azul)
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (0, 120, 215))
    return image

def setup_menu():
    url_master = get_ngrok_url(8501)
    
    menu_items = [
        pystray.MenuItem("🏠 Abrir Painel Local", abrir_navegador_local),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🔌 Desligar Acesso Online" if url_master else "⚡ Ligar Acesso Online", toggle_ngrok),
        pystray.MenuItem("🔄 REINICIAR SISTEMA COMPLETO", reiniciar_sistema),
        pystray.Menu.SEPARATOR,
    ]
    
    if url_master:
        menu_items.append(pystray.MenuItem("🌐 ACESSAR SISTEMA MASTER", lambda: webbrowser.open(url_master)))
    
    menu_items.extend([
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📍 IP Rede: " + get_network_url(), lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🔄 Reiniciar Sistema", reiniciar_sistema),
        pystray.MenuItem("❌ Sair do Sistema", stop_all)
    ])
    
    return pystray.Menu(*menu_items)

def atualizar_menu_periodicamente(icon):
    """Atualiza o menu da bandeja periodicamente para mostrar o status do Ngrok."""
    while True:
        time.sleep(3)
        icon.menu = setup_menu()

def auto_abrir_navegador():
    """Tenta detectar o servidor, faz um 'pre-warming' e abre o navegador em modo APP."""
    for _ in range(40): # Aumentado para dar tempo ao pre-warming
        if is_port_in_use(8501):
            # --- TECNICA DE PRE-WARMING ---
            # Faz uma chamada silenciosa ao servidor para disparar os caches iniciais
            # enquanto o usuário ainda está vendo a Splash Screen.
            try:
                requests.get('http://localhost:8501', timeout=2)
            except: pass
            
            time.sleep(2) # Pausa estratégica para o Streamlit terminar de processar o pre-warm
            abrir_navegador_local()
            break
        time.sleep(1)

def show_splash_screen():
    import tkinter as tk
    from tkinter import ttk
    try:
        from PIL import ImageTk
        splash = tk.Tk()
        splash.overrideredirect(True)
        splash.attributes('-topmost', True)
        
        window_width = 500
        window_height = 300
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = int((screen_width/2) - (window_width/2))
        y = int((screen_height/2) - (window_height/2))
        
        splash.geometry(f'{window_width}x{window_height}+{x}+{y}')
        splash.configure(bg='#020817') # Fundo escuro premium
        
        # Borda brilhante simulada
        frame = tk.Frame(splash, bg='#020817', highlightbackground='#38bdf8', highlightthickness=1)
        frame.place(relwidth=1, relheight=1)

        img = create_image()
        img = img.resize((100, 100))
        photo = ImageTk.PhotoImage(img)
        
        lbl_img = tk.Label(frame, image=photo, bg='#020817')
        lbl_img.image = photo
        lbl_img.pack(pady=(35, 10))
        
        tk.Label(frame, text="JUVICKS ELITE SERVER", font=("Inter", 20, "bold"), fg="#38bdf8", bg='#020817').pack()
        lbl_status = tk.Label(frame, text="Iniciando ecossistema...", font=("Inter", 10), fg="#94A3B8", bg='#020817')
        lbl_status.pack(pady=(5, 15))
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Premium.Horizontal.TProgressbar", 
                        thickness=6, 
                        background='#38bdf8', 
                        troughcolor='#1e293b', 
                        bordercolor='#020817',
                        lightcolor='#38bdf8',
                        darkcolor='#38bdf8')
        
        progress = ttk.Progressbar(frame, style="Premium.Horizontal.TProgressbar", orient="horizontal", length=350, mode="determinate")
        progress.pack()
        
        tk.Label(frame, text="v0.7.2 - OPERATIONAL SYSTEM", font=("JetBrains Mono", 7), fg="#475569", bg='#020817').pack(side="bottom", pady=10)

        splash.timeout = 0
        def check_ready():
            current_time = splash.timeout
            progress['value'] = min(98, (current_time / 25) * 100)
            
            steps = {
                2: "Injetando Motores Streamlit...",
                5: "Autenticando Base de Dados...",
                10: "Sincronizando Microserviços Zap...",
                15: "Validando Portas de Comunicação...",
                20: "Preparando Interface de Alta Fidelidade..."
            }
            if current_time in steps:
                lbl_status.config(text=steps[current_time])

            if is_port_in_use(8501):
                progress['value'] = 100
                lbl_status.config(text="Ecossistema pronto. Abrindo...")
                splash.update()
                splash.after(1000, lambda: [splash.quit(), splash.destroy()])
            elif current_time > 50:
                splash.after(500, lambda: [splash.quit(), splash.destroy()])
            else:
                splash.timeout += 1
                splash.after(400, check_ready)

        splash.after(400, check_ready)
        splash.mainloop()
    except Exception:
        pass

# --- 7. BLOCO DE EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    # 0. Suporte obrigatorio para PyInstaller (Multiprocessamento)
    multiprocessing.freeze_support()

    # Suporte para execução de scripts via -c (usado na conversão de PDF)
    if len(sys.argv) > 2 and sys.argv[1] == "-c":
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
            internal = os.path.join(base, "_internal")
            sys.path.append(base)
            sys.path.append(internal)
            sys.path.append(os.path.join(internal, "PY"))
        try:
            exec(sys.argv[2])
            sys.exit(0)
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

    try:
        # A) Verifica se estamos no modo SERVIDOR (Chamada do Streamlit)
        # Se for o servidor, apenas roda o streamlit.main() e NUNCA cria icone na bandeja.
        if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            import streamlit.web.cli as stcli
            stcli.main()
            sys.exit(0)
            
        # A.2) Verifica se estamos no modo SERVIDOR FLASK (Chamado via EXE congelado)
        if len(sys.argv) > 1 and sys.argv[1] == "flask":
            if getattr(sys, 'frozen', False):
                base = sys._MEIPASS
                internal = os.path.join(base, "_internal")
                sys.path.append(internal)
                sys.path.append(os.path.join(internal, "PY"))
            
            try:
                from assiname_app.app import app
                import argparse
                parser = argparse.ArgumentParser()
                parser.add_argument('--port', type=int, default=5001)
                args, _ = parser.parse_known_args()
                app.run(debug=False, host='0.0.0.0', port=args.port)
            except Exception as e:
                # Log de erro específico para a importação do Flask
                log_err = os.path.join(os.path.expanduser("~"), "Desktop", "ERRO_FLASK_START.txt")
                with open(log_err, "w", encoding="utf-8") as f:
                    import traceback
                    f.write(f"ERRO AO CARREGAR MÓDULO DE ASSINATURAS:\n{str(e)}\n\n")
                    f.write(traceback.format_exc())
                    f.write(f"\nSYS PATH: {sys.path}")
                sys.exit(1)
            sys.exit(0)

        # B) Se chegamos aqui, somos o LANÇADOR (O processo que cria o icone e o tray)
        # Protecao de Instancia Unica: Usamos um Mutex do Windows para evitar duplicidade
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\JUVICKS07_LAUNCH_MUTEX")
        if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
             sys.exit(0)
        
        # 1. Inicia os motores em segundo plano (Popen não bloqueia)
        start_streamlit()
        start_flask()
        
        # 2. Inicia thread para vigiar e abrir o navegador
        t_nav = threading.Thread(target=auto_abrir_navegador, daemon=True)
        t_nav.start()

        # 3. Mostra a Tela de Carregamento (Splash Screen)
        # IMPORTANTE: Tkinter deve rodar na thread principal.
        show_splash_screen()
        
        # 4. Inicia o Controle na Bandeja (Processo Pai Único)
        try:
            icon = pystray.Icon("JUVICKS07", create_image(), "JUVICKS07 - Gerenciador", setup_menu())
            thread = threading.Thread(target=atualizar_menu_periodicamente, args=(icon,), daemon=True)
            thread.start()
            
            # Iniciar motor WhatsApp
            threading.Thread(target=_ligar_whatsapp, daemon=True).start()
            
            icon.run()
        except:
            while True: time.sleep(1000)
                
    except Exception as e:
        # REGISTRA QUALQUER ERRO QUE IMPEÇA O SISTEMA DE ABRIR
        log_path = os.path.join(os.path.expanduser("~"), "Desktop", "ERRO_JUVICKS_START.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            import traceback
            f.write(f"ERRO CRITICO AO INICIAR:\n{str(e)}\n\n")
            f.write(traceback.format_exc())
        
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"O Sistema falhou ao iniciar.\nLog salvo na Área de Trabalho.\nErro: {str(e)}", "Erro Crítico - JUVICKS07", 0x10)
        except:
            pass
        sys.exit(1)
