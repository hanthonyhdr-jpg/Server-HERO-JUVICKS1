import os
import subprocess
import sys
import shutil
import re

# Configura o terminal para aceitar emojis se possível
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def imprimir_etapa(texto):
    print("\n" + "="*60)
    print(f">>> {texto.upper()}")
    print("="*60 + "\n")

# Caminho do projeto
ROOT = os.path.dirname(os.path.abspath(__file__))

def limpar_dados_sensiveis(root_dir):
    imprimir_etapa("Limpando dados sensíveis (Sessões e Logs)")
    
    arquivos_remover = [
        os.path.join(root_dir, 'PY', 'WHATSAPP_MOTOR', 'status.json'),
        os.path.join(root_dir, 'PY', 'WHATSAPP_MOTOR', 'motor.log'),
        os.path.join(root_dir, 'DATABASE', 'motor_zap.log'),
        os.path.join(root_dir, 'DATABASE', 'LOG_DB.txt'),
        os.path.join(root_dir, 'ngrok_dominio.txt'),
        os.path.join(root_dir, 'ngrok_temp.yml'),
        os.path.join(root_dir, 'LICENSA', 'license.key'),
        os.path.join(root_dir, 'PY', 'sessions', 'session_state.json'), # Novo: Limpa estados de sessão antigos
    ]
    
    diretorios_remover = [
        os.path.join(root_dir, 'PY', 'WHATSAPP_MOTOR', '.wwebjs_auth'),
        # NOTA: A pasta 'sessions/' NÃO deve ser removida para preservar auto-login
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'JUVICKS_DATA') # Limpa dados de teste locais
    ]
    
    # Remove apenas o last_session.json (credenciais de dev) mas mantém a estrutura
    sess_json = os.path.join(root_dir, 'PY', 'sessions', 'last_session.json')
    if os.path.exists(sess_json):
        try:
            os.remove(sess_json)
            print(f"[REMOVIDO] Sessão de desenvolvimento: {sess_json}")
        except: pass

    for arq in arquivos_remover:
        if os.path.exists(arq):
            try:
                os.remove(arq)
                print(f"[REMOVIDO] Arquivo: {arq}")
            except: pass

    for d in diretorios_remover:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"[REMOVIDO] Diretório: {d}")
            except: pass

def garantir_node_motor(root_dir):
    motor_dir = os.path.join(root_dir, 'PY', 'WHATSAPP_MOTOR')
    node_exe = os.path.join(motor_dir, 'node.exe')
    if os.path.exists(motor_dir) and not os.path.exists(node_exe):
        imprimir_etapa("Injetando Node.js Embutido (Portabilidade 100%)")
        print("Baixando node.exe stand-alone (aprox. 60MB)... Isso pode levar alguns minutos.")
        import urllib.request
        url = "https://nodejs.org/dist/v20.9.0/win-x64/node.exe"
        try:
            urllib.request.urlretrieve(url, node_exe)
            print("[OK] node.exe baixado com sucesso! O motor do Zap agora é portátil.")
        except Exception as e:
            print(f"[AVISO] Falha ao baixar node.exe: {e}")
            print("O instalador usará o Node instalado globalmente na máquina cliente.")

def configurar_branding(root_dir):
    imprimir_etapa("Configuração de Branding")
    
    spec_path = os.path.join(root_dir, "SISTEMA_JUVIKS_OFICIAL.spec")
    iss_path = os.path.join(root_dir, "instalador.iss")
    
    nome_atual_display = "JUVICKS SERVER"
    nome_atual_safe = "HERO_JUVICKS_SERVER_0_8"
    
    # Tenta detectar o nome atual no .spec
    if os.path.exists(spec_path):
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()
            match = re.search(r"name='([^']+)'", spec_content)
            if match:
                nome_atual_safe = match.group(1)

    # Tenta detectar o nome atual no .iss
    if os.path.exists(iss_path):
        with open(iss_path, 'r', encoding='utf-8') as f:
            iss_content = f.read()
            match = re.search(r"AppName=([^\r\n]+)", iss_content)
            if match:
                nome_atual_display = match.group(1)
    
    print(f"Nome atual detectado: {nome_atual_display}")
    print(f"Nome interno detectado: {nome_atual_safe}")
    
    novo_nome = input("\nDigite o NOVO NOME do seu sistema (ou Enter para manter): ").strip()
    
    if not novo_nome:
        print("[!] Mantendo nomes atuais.")
        return nome_atual_display, nome_atual_safe

    # Gerar nome "safe" (sem espaços e caracteres especiais)
    novo_nome_safe = re.sub(r'[^a-zA-Z0-9]', '_', novo_nome).upper()
    
    print(f"\n[+] Novo Nome Exibido: {novo_nome}")
    print(f"[+] Novo Nome Interno: {novo_nome_safe}")
    
    # 1. Atualizar o arquivo .spec
    if os.path.exists(spec_path):
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui o nome no EXE e no COLLECT (todas as ocorrências de name='...')
        content = re.sub(r"name='[^']+'", f"name='{novo_nome_safe}'", content)
        
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Arquivo .spec atualizado.")

    # 2. Atualizar o arquivo .iss
    if os.path.exists(iss_path):
        with open(iss_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituições inteligentes no .iss usando Regex para ser mais robusto
        content = re.sub(r"AppName=[^\r\n]+", f"AppName={novo_nome}".replace("\\", "\\\\"), content)
        content = re.sub(r"DefaultDirName=\{commonpf\}\\[^\r\n]+", f"DefaultDirName={{commonpf}}\\{novo_nome.replace(' ', '')}".replace("\\", "\\\\"), content)
        content = re.sub(r"OutputBaseFilename=Instalador_[^\r\n]+", f"OutputBaseFilename=Instalador_{novo_nome.replace(' ', '')}_OFICIAL".replace("\\", "\\\\"), content)
        
        # Substitui o nome do executável (UninstallDisplayIcon)
        content = re.sub(r"UninstallDisplayIcon=\{app\}\\[^\r\n]+\.exe", f"UninstallDisplayIcon={{app}}\\{novo_nome_safe}.exe".replace("\\", "\\\\"), content)
        
        # Substitui a pasta de origem no dist
        content = re.sub(r"Source: \"dist\\[^\\]+\\\*\"", f'Source: "dist\\{novo_nome_safe}\\*"'.replace("\\", "\\\\"), content)
        
        # Garante que o OutputDir esteja correto
        if "OutputDir=" not in content:
            content = re.sub(r"\[Setup\]", "[Setup]\nOutputDir=Output", content)
        else:
            content = re.sub(r"OutputDir=[^\r\n]+", "OutputDir=Output", content)

        # Atalhos e referências extras
        content = re.sub(r"Name: \"\{group\}\\[^\"]+\"", f"Name: \"{{group}}\\{novo_nome}\"".replace("\\", "\\\\"), content)
        content = re.sub(r"Name: \"\{autodesktop\}\\[^\"]+\"", f"Name: \"{{autodesktop}}\\{novo_nome}\"".replace("\\", "\\\\"), content)
        
        content = re.sub(r"Filename: \"\{app\}\\[^\"]+\.exe\"", f'Filename: "{{app}}\\{novo_nome_safe}.exe"'.replace("\\", "\\\\"), content)
        content = re.sub(r"ValueName: \"[^\"]+\"", f'ValueName: "{novo_nome_safe}"', content)
        
        # Limpa qualquer ValueData antigo e coloca o novo padrão com aspas triplas e flags
        content = re.sub(r"ValueData: [^\r\n]+", f'ValueData: """{{app}}\\{novo_nome_safe}.exe"""; Flags: uninsdeletevalue; Tasks: startup'.replace("\\", "\\\\"), content)
        
        with open(iss_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Arquivo .iss atualizado.")
        
    return novo_nome, novo_nome_safe


def verificar_integridade_modulos(root_dir):
    imprimir_etapa("Verificando integridade dos módulos vitais")
    arquivos_vitais = [
        os.path.join(root_dir, 'PY', 'pages', '02_Gerar_Orcamentos.py'),
        os.path.join(root_dir, 'PY', 'utils', 'documentos.py'),
        os.path.join(root_dir, 'SISTEMA_JUVIKS_OFICIAL.spec'),
        os.path.join(root_dir, 'MODELOS_HTML', 'dashboard_moderno.html'),
        os.path.join(root_dir, 'MODELOS_HTML', 'comprovante_premium.html')
    ]
    for arq in arquivos_vitais:
        if not os.path.exists(arq):
            print(f"❌ ERRO CRÍTICO: Arquivo não encontrado: {arq}")
            sys.exit(1)
    print("✅ Todos os módulos de orçamento e PDF detectados.")


def main():
    # Obtém o diretório real onde o script está localizado
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    imprimir_etapa("Iniciando Processo de Compilação Inteligente")

    # 1. Verificação de integridade dos módulos vitais
    verificar_integridade_modulos(root_dir)

    # 2. Configuração de Nome/Branding (Interativo)
    display_name, safe_name = configurar_branding(root_dir)

    # 3. Sincronização do HTML de Login (CRÍTICO para o executável)
    imprimir_etapa("Sincronizando Interface de Login")
    html_src  = os.path.join(root_dir, 'nova', 'hero_juvicks_login_v3.html')
    html_dest = os.path.join(root_dir, 'PY', 'TEMAS', 'login_html.py')
    
    if os.path.exists(html_src):
        try:
            with open(html_src, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Sanitização básica para evitar quebra de string no Python
            with open(html_dest, 'w', encoding='utf-8') as f:
                f.write('# -*- coding: utf-8 -*-\n')
                f.write('# AUTO-GERADO por compilar_sistema.py - NAO EDITAR MANUALMENTE\n')
                f.write('LOGIN_HTML = ' + repr(html_content) + '\n')
            print(f"[OK] login_html.py atualizado com sucesso ({len(html_content)} bytes)")
        except Exception as e:
            print(f"[ERRO] Falha ao sincronizar HTML: {e}")
            sys.exit(1)
    else:
        print(f"[AVISO] HTML de login original não encontrado em {html_src}. Usando versão atual de TEMAS.")

    # 4. Preparação de pastas e limpeza de dados sensíveis
    sessions_dir = os.path.join(root_dir, 'PY', 'sessions')
    os.makedirs(sessions_dir, exist_ok=True)
    if not os.path.exists(os.path.join(sessions_dir, '.gitkeep')):
        open(os.path.join(sessions_dir, '.gitkeep'), 'w').close()
    
    limpar_dados_sensiveis(root_dir)
    garantir_node_motor(root_dir)

    # 5. Limpeza de builds antigos
    imprimir_etapa("Limpando ambiente de build")
    for d in ['build', 'dist', 'Output']:
        p = os.path.join(root_dir, d)
        if os.path.exists(p):
            try: shutil.rmtree(p)
            except: pass
            print(f"[LIMPO] Pasta: {d}")
    
    # Recria a pasta Output para garantir que o Inno Setup tenha onde salvar
    os.makedirs(os.path.join(root_dir, "Output"), exist_ok=True)

    # 6. Execução do PyInstaller
    imprimir_etapa(f"Compilando Executável: {display_name}")
    spec_file = "SISTEMA_JUVIKS_OFICIAL.spec"
    
    # Tenta usar o python do venv se disponível
    py_exec = sys.executable
    venv_py = os.path.join(root_dir, 'venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_py):
        py_exec = venv_py
        print(f"[VENV] Usando Python do ambiente virtual: {py_exec}")

    pyinstaller_cmd = [py_exec, "-m", "PyInstaller", "--clean", "-y", spec_file]
    
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print(f"\n✅ EXECUTÁVEL '{safe_name}.exe' GERADO COM SUCESSO!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO NO PYINSTALLER: {e}")
        sys.exit(1)

    # 7. Geração do Instalador (Inno Setup)
    imprimir_etapa("Gerando Instalador Final (.exe de instalação)")
    iss_file = "instalador.iss"
    
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    ]
    
    iscc = next((p for p in inno_paths if os.path.exists(p)), None)
    
    if iscc and os.path.exists(iss_file):
        try:
            subprocess.run([iscc, iss_file], check=True)
            print("\n" + "="*60)
            print(f">>> SISTEMA '{display_name.upper()}' PRONTO PARA DISTRIBUIÇÃO!")
            print(">>> Localização: pasta 'Output'")
            print("="*60 + "\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ ERRO NO INNO SETUP: {e}")
    else:
        print("[AVISO] Inno Setup não encontrado. O instalador .iss não foi gerado.")
        print("        O executável portátil está disponível na pasta 'dist'.")

if __name__ == "__main__":
    main()

