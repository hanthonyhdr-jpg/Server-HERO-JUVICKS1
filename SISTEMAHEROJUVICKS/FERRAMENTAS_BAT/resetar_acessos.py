import sqlite3
import os
import sys

# Permite as importações a partir da base do sistema
# --- LÓGICA DE LOCALIZAÇÃO ROBUSTA (MESMA DO DATABASE.PY) ---
def get_safe_base_dir():
    try:
        # Se estivermos rodando de dentro de FERRAMENTAS_BAT, precisamos do pai
        _current = os.path.dirname(os.path.abspath(__file__))
        _root = os.path.dirname(_current)
        
        # Se estivermos em um ambiente congelado (EXE) ou instalado
        app_dir = _root
        if "Program Files" in app_dir or "Arquivos de Programas" in app_dir:
            appdata_juvicks = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "JUVICKS_DATA")
            if os.path.exists(appdata_juvicks):
                return appdata_juvicks
        return _root
    except:
        return os.getcwd()

base_dir = get_safe_base_dir()
db_path = os.path.normpath(os.path.join(base_dir, "DATABASE", "sistema_vendas.db"))

# Permite as importações a partir da base do sistema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PY.utils.hardware_license import registrar_computador, apagar_registro_total
except ImportError:
    print("Erro ao carregar os modulos de licenca do Juviks.")
    sys.exit(1)

print("\n--- FORCANDO REESCRITA DE CREDENCIAIS ---")
usr = input("-> Novo Usuario Master (ex: admin): ").strip()
pwd = input("-> Nova Senha de Acesso: ").strip()
key = input("-> Nova Chave Mestra / Licenca: ").strip()

if not usr or not pwd:
    print("\n[!] Operacao cancelada: Usuario e Senha requeridos.")
    sys.exit(1)

print("\n[+] Varrendo e Quebrando travas de seguranca antigas do PC...")
apagar_registro_total()

print("[+] Assinando Hardware atual com sua nova CHAVE MESTRA...")
registrar_computador(usr, pwd, key)

print(f"[+] Reestruturando base de dados em: {db_path}...")

try:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Cria a tabela caso não exista logicamente
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    usuario TEXT UNIQUE, 
                    senha TEXT, 
                    nivel_acesso TEXT
                )''')
    
    # Detona tudo que havia de administradores e usuários para focar no novo
    cursor.execute("DELETE FROM usuarios")
    cursor.execute("INSERT INTO usuarios (usuario, senha, nivel_acesso) VALUES (?, ?, ?)", (usr, pwd, "ADMIN"))
    
    try:
        cursor.execute("DELETE FROM sessoes_ativas")
    except:
        pass

    conn.commit()
    conn.close()
    
    print("\n==================================")
    print(" SUPER RESET CONCLUIDO COM SUCESSO!")
    print("==================================")
    print(f" [+] Sistema vinculado ao Usuario: {usr}")
    print(" [+] Permissoes Totais (ADMIN) Concedidas.")
    print(" [+] Pode iniciar o Painel Livremente agora.")
    
except Exception as e:
    print(f"\n[!] Falha grave ao alterar banco de dados: {e}")
