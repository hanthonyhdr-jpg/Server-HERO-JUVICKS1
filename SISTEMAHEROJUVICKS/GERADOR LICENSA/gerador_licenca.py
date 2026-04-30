import hashlib
import subprocess
import os

# 🔑 COLOQUE A MESMA CHAVE MESTRA QUE ESTÁ NO SISTEMA
MASTER_SECRET = "JUVIKS_2026_HERO_SECURE_VAULT"

def gerar_chave_para_o_cliente(hwid_cliente):
    """Gera a Licença Final baseada no HWID fornecido pelo cliente."""
    # Combina o HWID do cliente com o SEU Segredo Mestre
    raw_key = hashlib.sha256(f"{hwid_cliente}{MASTER_SECRET}".encode()).hexdigest().upper()[:16]
    # Formata como XXXX-XXXX-XXXX-XXXX
    return f"{raw_key[:4]}-{raw_key[4:8]}-{raw_key[8:12]}-{raw_key[12:]}"

def menu_gerador():
    """Interface simples de linha de comando para você gerar as chaves."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==================================================================")
    print("        🛠️  GERADOR DE LICENÇAS POR HARDWARE - JUVIKS07         ")
    print("==================================================================")
    print("\nINSTRUÇÕES:")
    print("1. Peça ao cliente para abrir o sistema.")
    print("2. Ele verá uma tela vermelha com um 'ID de Hardware'.")
    print("3. Ele deve te passar o ID (Ex: ABCD-EFGH-IJKL).")
    print("4. Cole o ID abaixo para gerar a chave de ativação dele.\n")
    
    hwid = input("👉 DIGITE O ID DE HARDWARE DO CLIENTE: ").strip().upper()
    
    if len(hwid) < 10:
        print("\n❌ ID INVÁLIDO! O ID deve ter cerca de 12 caracteres (ex: XXXX-XXXX-XXXX).")
    else:
        chave = gerar_chave_para_o_cliente(hwid)
        print("\n" + "="*50)
        print(f"✅ CHAVE GERADA COM SUCESSO!")
        print(f"🔑 CHAVE: {chave}")
        print("="*50)
        print("\nBasta que o cliente cole esta chave na tela de bloqueio e clique em ATIVAR.")

    print("\n")
    input("Pressione Enter para fechar...")

if __name__ == "__main__":
    menu_gerador()
