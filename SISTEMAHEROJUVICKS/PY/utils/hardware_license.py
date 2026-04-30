import subprocess
import hashlib
import os
import json
import base64
from datetime import datetime

def get_full_hwid():
    """Gera identificador ultra-seguro baseado em Disco, Memória e Placa-Mãe."""
    import subprocess
    ids = []
    
    # 1. Serial do HD/SSD (Via PowerShell)
    try:
        out = subprocess.check_output('powershell -Command "Get-CimInstance -ClassName Win32_DiskDrive | Select-Object -ExpandProperty SerialNumber"', shell=True).decode(errors='ignore')
        for s in out.splitlines():
            if s.strip(): ids.append(s.strip())
    except: pass

    # 2. Serial das Memórias RAM (Via PowerShell)
    try:
        out = subprocess.check_output('powershell -Command "Get-CimInstance -ClassName Win32_PhysicalMemory | Select-Object -ExpandProperty SerialNumber"', shell=True).decode(errors='ignore')
        for s in out.splitlines():
            if s.strip(): ids.append(s.strip())
    except: pass

    # 3. Serial da Placa-Mãe
    try:
        out = subprocess.check_output('powershell -Command "Get-CimInstance -ClassName Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber"', shell=True).decode(errors='ignore')
        for s in out.splitlines():
            if s.strip() and "To be filled" not in s: ids.append(s.strip())
    except: pass

    ids.append(os.environ.get('COMPUTERNAME', 'juv-pc'))
    raw_str = "|".join(sorted(list(set(ids)))) # Ordena para garantir consistência
    return hashlib.sha224(raw_str.encode()).hexdigest().upper()[:32]

# --- LOCALIZAÇÃO DA TRAVA NO DISCO C: ---
# Tentamos usar uma pasta comum a todos os usuários para persistência total
_CONFIG_DIR = "C:/JUVIKS_AUTH_DATABASE"
if not os.path.exists(_CONFIG_DIR):
    try: os.makedirs(_CONFIG_DIR, exist_ok=True)
    except: _CONFIG_DIR = os.path.join(os.path.expanduser("~"), "JUVIKS_AUTH") # Fallback se C: falhar

_ID_FILE = os.path.join(_CONFIG_DIR, "secure_hardware_vault.json")

def enc(txt): return base64.b64encode(txt.encode()).decode()
def dec(txt): return base64.b64decode(txt.encode()).decode()

def registrar_computador(usuario, senha, chave):
    """Adiciona ou atualiza um perfil de usuário neste computador."""
    try:
        if not os.path.exists(_CONFIG_DIR):
            os.makedirs(_CONFIG_DIR, exist_ok=True)
        
        perfis = {}
        if os.path.exists(_ID_FILE):
            with open(_ID_FILE, "r", encoding="utf-8") as f:
                perfis = json.load(f)
        
        hwid = get_full_hwid()
        # Armazena por usuário para permitir múltiplos
        perfis[usuario] = {
            "senha": enc(senha),
            "chave": enc(chave),
            "hwid": hwid,
            "ultima_vez": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        with open(_ID_FILE, "w", encoding="utf-8") as f:
            json.dump(perfis, f, indent=4)
        return True
    except:
        return False

def listar_perfis_autorizados():
    """Retorna lista de usuários que têm acesso salvo neste hardware."""
    if not os.path.exists(_ID_FILE):
        return []
    
    try:
        with open(_ID_FILE, "r", encoding="utf-8") as f:
            perfis = json.load(f)
        
        atual_hwid = get_full_hwid()
        autorizados = []
        for user, dados in perfis.items():
            if dados.get("hwid") == atual_hwid:
                autorizados.append(user)
        return autorizados
    except:
        return []

def carregar_credenciais_perfil(usuario):
    """Recupera dados de um usuário específico se o hardware bater."""
    try:
        with open(_ID_FILE, "r", encoding="utf-8") as f:
            perfis = json.load(f)
        
        dados = perfis.get(usuario)
        if dados and dados.get("hwid") == get_full_hwid():
            return usuario, dec(dados["senha"]), dec(dados["chave"])
    except:
        pass
    return None, None, None

def apagar_perfil(usuario):
    """Remove apenas um usuário específico do computador."""
    if not os.path.exists(_ID_FILE): return False
    try:
        with open(_ID_FILE, "r", encoding="utf-8") as f:
            perfis = json.load(f)
        if usuario in perfis:
            del perfis[usuario]
            with open(_ID_FILE, "w", encoding="utf-8") as f:
                json.dump(perfis, f, indent=4)
            return True
    except: pass
    return False

def apagar_registro_total():
    """Limpa todos os perfis do computador."""
    if os.path.exists(_ID_FILE):
        os.remove(_ID_FILE)
        return True
    return False
