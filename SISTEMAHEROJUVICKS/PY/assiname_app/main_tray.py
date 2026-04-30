import pystray
from PIL import Image
import subprocess
import os
import sys
import threading
import time
import webbrowser
import requests
import pyperclip

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLASK_APP = os.path.join(BASE_DIR, "app.py")
NGROK_EXE = os.path.join(BASE_DIR, "ngrok.exe")
ICON_PATH = os.path.join(BASE_DIR, "icon.png")

# Globais
flask_proc = None
ngrok_proc = None
public_url = None

def start_flask():
    global flask_proc
    if flask_proc is None:
        flask_proc = subprocess.Popen([sys.executable.replace("python.exe", "pythonw.exe"), FLASK_APP], 
                                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

def stop_flask():
    global flask_proc
    if flask_proc:
        flask_proc.terminate()
        flask_proc = None

def start_ngrok():
    global ngrok_proc, public_url
    if ngrok_proc is None:
        try:
            ngrok_proc = subprocess.Popen(["ngrok", "http", "5000"], 
                                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            threading.Thread(target=fetch_ngrok_url).start()
        except Exception as e:
            print(f"Erro Ngrok: {e}")

def fetch_ngrok_url():
    global public_url
    time.sleep(3)
    for _ in range(5):
        try:
            res = requests.get("http://127.0.0.1:4040/api/tunnels")
            data = res.json()
            public_url = data['tunnels'][0]['public_url']
            break
        except:
            time.sleep(2)

def stop_ngrok():
    global ngrok_proc, public_url
    if ngrok_proc:
        ngrok_proc.terminate()
        ngrok_proc = None
        public_url = None

def on_open_local(icon, item):
    webbrowser.open("http://127.0.0.1:5000")

def on_open_public(icon, item):
    global public_url
    if public_url:
        webbrowser.open(public_url)
    else:
        icon.notify("Acesso Online não detectado ainda.", "ASSINA HD")

def on_copy_public(icon, item):
    global public_url
    if public_url:
        pyperclip.copy(public_url)
        icon.notify(f"Link Copiado: {public_url}", "ASSINA HD")
    else:
        icon.notify("Link ainda não disponível.", "ASSINA HD")

def on_toggle_online(icon, item):
    global ngrok_proc
    if ngrok_proc:
        stop_ngrok()
        icon.notify("Acesso Online DESATIVADO", "ASSINA HD")
    else:
        start_ngrok()
        icon.notify("Iniciando Acesso Online...", "ASSINA HD")

def on_exit(icon, item):
    stop_flask()
    stop_ngrok()
    icon.stop()

def run_tray():
    if not os.path.exists(ICON_PATH):
        image = Image.new('RGB', (64, 64), color=(79, 70, 229))
    else:
        image = Image.open(ICON_PATH)

    def get_online_label(item):
        return "DESABILITAR ACESSO" if ngrok_proc else "HABILITAR ACESSO"

    menu = pystray.Menu(
        pystray.MenuItem("ENTRAR NO PAINEL LOCAL", on_open_local),
        pystray.MenuItem(get_online_label, on_toggle_online),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("COPIAR LINK PÚBLICO (KABAN)", on_copy_public, enabled=lambda item: public_url is not None),
        pystray.MenuItem("ABRIR LINK PÚBLICO (KABAN)", on_open_public, enabled=lambda item: public_url is not None),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("SAIR", on_exit)
    )

    icon = pystray.Icon("AssinaHD", image, "ASSINA HD - Sistema de Assinatura", menu)
    start_flask()
    icon.run()

if __name__ == "__main__":
    run_tray()
