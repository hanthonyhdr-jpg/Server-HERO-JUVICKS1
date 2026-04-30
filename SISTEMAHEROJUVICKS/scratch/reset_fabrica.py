import os
import shutil
import sqlite3
import json

def factory_reset():
    print("=== INICIANDO PROTOCOLO LIMPO DE FÁBRICA ===")
    
    # 1. Limpar pastas de dados locais do desenvolvedor
    app_data = os.path.join(os.environ.get('LOCALAPPDATA', ''), "JUVICKS_DATA")
    if os.path.exists(app_data):
        print(f"Limpando dados locais: {app_data}")
        shutil.rmtree(app_data)
    
    # 2. Limpar sessões e logs no projeto
    paths_to_clean = [
        'PY/sessions',
        'PY/WHATSAPP_MOTOR/.wwebjs_auth',
        'PY/WHATSAPP_MOTOR/motor.log',
        'PY/WHATSAPP_MOTOR/status.json',
        'DATABASE/motor_zap.log',
        'LICENSA/license.key'
    ]
    for p in paths_to_clean:
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            print(f"Removido: {p}")

    # 3. Resetar o Banco de Dados para estado 'Virgem'
    # Se usar PostgreSQL, vamos avisar que as tabelas devem ser truncadas manualmente ou via script
    config_path = 'CONFIG_SISTEMA/db_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        
        if cfg.get('engine') == 'postgresql':
            print("\n[AVISO] O sistema está configurado para PostgreSQL.")
            print("Para um 'Limpo de Fábrica' total, você deve limpar as tabelas no seu servidor PostgreSQL.")
            print("Deseja que eu tente limpar as tabelas agora? (S/N)")
            # Como estamos em script, vamos apenas oferecer a função se o usuário importar
    
    print("\n[OK] Ambiente de desenvolvimento limpo!")
    print("Agora você pode rodar a Opção 11 para gerar um instalador 'virgem'.")

if __name__ == "__main__":
    factory_reset()
