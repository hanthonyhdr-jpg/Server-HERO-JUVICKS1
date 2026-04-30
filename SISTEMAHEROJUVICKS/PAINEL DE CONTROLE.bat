@echo off
setlocal enabledelayedexpansion

:: ══════════════════════════════════════════════════════════════════════════
:: CONFIGURAÇÃO DE AMBIENTE
:: ══════════════════════════════════════════════════════════════════════════
SET "BASE_DIR=%~dp0"
CD /D "%BASE_DIR%"
SET "VENV_PYTHON=%BASE_DIR%venv\Scripts\python.exe"
SET "VENV_PYTHONW=%BASE_DIR%venv\Scripts\pythonw.exe"
SET "STREAMLIT=%BASE_DIR%venv\Scripts\streamlit.exe"

if /I "%~1"=="GUI" (
    echo [+] Subindo servidor API para painel HTML...
    if exist "%VENV_PYTHON%" (
        start "" "%VENV_PYTHON%" painel_server.py
    ) else (
        start "" python painel_server.py
    )
    timeout /t 2 >nul
    start "" "http://localhost:8089"
    exit /b
)

if "%~1" neq "" (
    set "opcao=%~1"
    set "AUTO_MODE=1"
    goto ROUTING
)

:MENU
set "opcao="
color 0F
cls
echo.
echo   ================================================================
echo             JUVIKS HERO 07 - PAINEL DE CONTROLE MASTER            
echo   ================================================================
echo.
echo   [ INICIALIZACAO E EXECUCAO ]
echo   1.  INICIAR SISTEMA (BACKGROUND)
echo   2.  FINALIZAR TODOS OS PROCESSOS
echo.
echo   [ FERRAMENTAS ADMINISTRATIVAS ]
echo   3.  PAINEL DE CONTROLE (RESET/MANUTENCAO/LOGS)
echo   4.  GERENCIADOR DE LICENCAS (HARDWARE ID)
echo   5.  EDITOR DE TEMAS E BRANDING
echo   6.  GERENCIADOR DE ACESSOS EXTERNOS
echo.
echo   [ DADOS E MANUTENCAO PRO ]
echo   7.  BACKUP DE SEGURANCA (INSTANTE)
echo   8.  VERIFICAR LOGS DE ERRO E BANCO
echo   9.  LIMPAR CACHE E TEMPORARIOS
echo.
echo   [ CONFIGURACAO E AMBIENTE ]
echo   10. CONFIGURAR ACESSO ONLINE (NGROK)
echo   11. COMPILAR PARA EXECUTAVEL (.EXE)
echo   12. REPARAR AMBIENTE (VENV/DEPENDENCIAS)
echo   13. TESTAR INTEGRIDADE DO SISTEMA
echo   14. LIMPAR TODAS AS DEPENDENCIAS
echo   15. ABRIR NOVA INTERFACE GRAFICA (GUI)
echo   16. GERAR SOMENTE INSTALADOR (ISS)
echo   17. SIMULAR CLIENTE (LIMPAR LICENCA)
echo.
echo   0.  SAIR DO PAINEL
echo.
echo   ----------------------------------------------------------------
set /p opcao="   Digite sua escolha: "

:ROUTING
if "%opcao%"=="1" goto INICIAR
if "%opcao%"=="2" goto PARAR
if "%opcao%"=="3" goto PAINEL_MASTER
if "%opcao%"=="4" goto LICENSA
if "%opcao%"=="5" goto THEME
if "%opcao%"=="6" goto GERENCIADOR
if "%opcao%"=="7" goto BACKUP
if "%opcao%"=="8" goto LOGS
if "%opcao%"=="9" goto LIMPAR
if "%opcao%"=="10" goto NGROK
if "%opcao%"=="11" goto EXE
if "%opcao%"=="12" goto VENV
if "%opcao%"=="13" goto TESTAR
if "%opcao%"=="14" goto LIMPAR_DEP
if "%opcao%"=="15" goto LANCHAR_GUI
if "%opcao%"=="16" goto ISS
if "%opcao%"=="17" goto CLEAN_LICENSE
if "%opcao%"=="0" exit
if defined AUTO_MODE (
    echo.
    echo [OK] Tarefa encaminhada pelo Painel GUI concluida! Fechando...
    timeout /t 3 >nul
    exit /b
)
goto MENU

:INICIAR
cls
echo.
echo   [+] Verificando ambiente virtual...
if not exist "%VENV_PYTHONW%" goto NO_VENV
echo   [+] Verificando scripts criticos...
if not exist "PY\launcher.py" (
    echo   [ERRO] PY\launcher.py nao encontrado!
    pause
    goto MENU
)
echo   [+] Iniciando motor JUVICKS07 em background...
start "" "%VENV_PYTHONW%" "PY\launcher.py"
echo   [OK] O icone aparecera na bandeja em instantes.
timeout /t 3 >nul
goto MENU

:PARAR
cls
echo.
echo   [!] INTERROMPENDO TODOS OS COMPONENTES DO JUVIKS...
echo.
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM streamlit.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1
taskkill /F /IM SISTEMA_JUVIKS_OFICIAL.exe /T >nul 2>&1
echo.
echo   [OK] Sistema interrompido e memoria limpa!
pause
goto MENU

:NGROK
cls
echo.
echo   [WEB ACCESS] CONFIGURACOES DO NGROK
echo   1. Vincular Token de Autenticacao (Primeiro Acesso)
echo   2. Definir um Dominio Customizado (Ex: sistema.ngrok-free.app)
echo   3. Remover Dominio Customizado
echo   0. Voltar ao Menu
echo.
set /p escolha_n="   O que deseja fazer? "

if "%escolha_n%"=="1" (
    echo.
    set /p token="   Cole seu Token: "
    set token=!token:ngrok config add-authtoken =!
    set token=!token:ngrok.exe config add-authtoken =!
    set token=!token:"=!
    if exist "ngrok.exe" (
        .\ngrok.exe config add-authtoken "!token!"
        echo   [OK] Acesso remoto configurado.
    ) else (
        echo   [ERRO] Arquivo ngrok.exe ausente na pasta raiz.
    )
) else if "%escolha_n%"=="2" (
    echo.
    echo   [!] Primeiro, va em dashboard.ngrok.com/cloud-edge/domains
    echo   [!] Crie um dominio estatico e cole ele abaixo.
    set /p dominio="   Cole seu dominio (Ex: app-nome.ngrok-free.app): "
    echo !dominio! > "ngrok_dominio.txt"
    echo   [OK] Dominio salvo com sucesso! O proximo acesso online usara este link.
) else if "%escolha_n%"=="3" (
    if exist "ngrok_dominio.txt" del /q "ngrok_dominio.txt"
    echo   [OK] Dominio removido. Voltou a ser aleatorio.
)

pause
goto MENU

:EXE
cls
echo.
echo   [BUILDER] Compilando para EXE Completo (PyInstaller + ISS)...
if not exist "%VENV_PYTHON%" goto NO_VENV
if not exist "compilar_sistema.py" (
    echo   [ERRO] Arquivo compilar_sistema.py ausente.
    pause
    goto MENU
)
"%VENV_PYTHON%" "compilar_sistema.py"
pause
goto MENU

:ISS
cls
echo.
echo   [BUILDER] Gerando SOMENTE o Instalador (ISS)...
if not exist "%VENV_PYTHON%" goto NO_VENV
if not exist "compilar_sistema.py" (
    echo   [ERRO] Arquivo compilar_sistema.py ausente.
    pause
    goto MENU
)
"%VENV_PYTHON%" "compilar_sistema.py"
pause
goto MENU

:THEME
cls
echo.
echo   [DESIGN] Editor de Estilo e Branding...
if not exist "%VENV_PYTHON%" goto NO_VENV
start "" "%VENV_PYTHON%" -m streamlit run "EDITOR_DE_TEMA\editor_tema.py" --server.port 8502 --server.headless true
echo   [OK] Painel de temas ativo na porta 8502.
timeout /t 3 >nul
goto MENU

:PAINEL_MASTER
cls
echo.
echo   [!] ABRINDO PAINEL DE CONTROLE MASTER...
if not exist "%VENV_PYTHON%" goto NO_VENV
start "" "%VENV_PYTHON%" -m streamlit run "PY\pages\98_98-Painel_Controle.py" --server.port 8501 --server.headless true
echo   [OK] Painel carregando na porta 8501.
timeout /t 3 >nul
goto MENU

:GERENCIADOR
cls
echo.
echo   [SECURITY] Gestor de Ativacoes e Seguranca...
if not exist "%VENV_PYTHON%" goto NO_VENV
start "" "%VENV_PYTHON%" -m streamlit run "PY\gerenciador_externo.py" --server.port 8503 --server.headless true
echo   [OK] Gerenciador ativo na porta 8503.
timeout /t 3 >nul
goto MENU

:LICENSA
cls
echo.
echo   [LICENSE] Gerador de Chaves de Licenciamento...
if not exist "%VENV_PYTHON%" goto NO_VENV
if exist "GERADOR LICENSA\gerador_licenca.py" (
    "%VENV_PYTHON%" "GERADOR LICENSA\gerador_licenca.py"
) else (
    echo [ERRO] Script gerador nao encontrado.
)
pause
goto MENU

:BACKUP
cls
echo.
echo   [DATA] Sistema de Copia de Seguranca...
if not exist "%VENV_PYTHON%" goto NO_VENV
"%VENV_PYTHON%" -m streamlit run "PY\backup_auto.py"
pause
goto MENU

:VENV
cls
echo.
echo   [SYSTEM] ATENCAO: Isso ira reconstruir o ambiente de bibliotecas.
if defined AUTO_MODE goto BYPASS_VENV_CONFIRM
set /p conf="   Confirma reconstrucao completa? (S/N): "
if /i "%conf%" neq "s" goto MENU

:BYPASS_VENV_CONFIRM
echo   [+] Removendo diretorio venv...
rd /s /q venv >nul 2>&1
echo   [+] Instalando Python VENV (requer Python no PATH)...
python -m venv venv
if errorlevel 1 (
    echo   [ERRO] Falha ao criar venv. Verifique se o Python esta instalado.
    pause
    goto MENU
)
echo   [+] Atualizando PIP e Instalando Dependencias...
"%VENV_PYTHON%" -m pip install --upgrade pip
"%VENV_PYTHON%" -m pip install -r "CONFIG_SISTEMA\requirements.txt"
echo   [+] Configurando extensoes do Windows...
if exist "%BASE_DIR%venv\Scripts\pywin32_postinstall.py" (
    "%VENV_PYTHON%" "%BASE_DIR%venv\Scripts\pywin32_postinstall.py" -install >nul 2>&1
)
echo   [OK] Ambiente pronto para uso!
pause
goto MENU

:LOGS
cls
echo.
echo   [LOGS] Historico de operacoes e erros:
if exist "LOG_DB.txt" (
    type "LOG_DB.txt"
) else (
    echo   [INFO] Banco de dados operando sem erros registrados.
)
echo.
echo   [BANCOS DETECTADOS]
dir /b "DATABASE\*.db" 2>nul
echo.
pause
goto MENU

:TESTAR
cls
echo.
echo   [DEBUG] Verificacao de Integridade do Sistema...
if not exist "%VENV_PYTHON%" (
    echo   [FALHA] Python no VENV: NAO ENCONTRADO
) else (
    for /f "tokens=*" %%i in ('"%VENV_PYTHON%" --version') do set ver=%%i
    echo   [OK] Python no VENV: !ver!
)
if not exist "%STREAMLIT%" (
    echo   [FALHA] Streamlit: NAO ENCONTRADO
) else (
    echo   [OK] Streamlit: LOCALIZADO
)
echo.
echo   [ARQUIVOS ESSENCIAIS]
if exist "PY\Inicio.py" (echo   [OK] PY\Inicio.py) else (echo   [FALHA] PY\Inicio.py)
if exist "PY\launcher.py" (echo   [OK] PY\launcher.py) else (echo   [FALHA] PY\launcher.py)
if exist "CONFIG_SISTEMA\requirements.txt" (echo   [OK] requirements.txt) else (echo   [FALHA] requirements.txt)
if exist "DATABASE\sistema_vendas.db" (echo   [OK] Banco Principal) else (echo   [!] Banco Principal nao criado ainda)
echo.
pause
goto MENU

:LIMPAR
cls
echo.
echo   [CLEAN] Removendo arquivos temporarios e cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo   [OK] Cache __pycache__ removido com sucesso.
pause
goto MENU

:LIMPAR_DEP
cls
echo.
echo   [CLEAN_ALL] Removendo todas as dependencias (VENV, Node Modules, Builds)...
echo   [+] Removendo ambiente virtual (venv)...
if exist "venv" rd /s /q "venv" >nul 2>&1
echo   [+] Removendo Node Modules...
if exist "node_modules" rd /s /q "node_modules" >nul 2>&1
echo   [+] Removendo pasta dist...
if exist "dist" rd /s /q "dist" >nul 2>&1
echo   [+] Removendo pasta build...
if exist "build" rd /s /q "build" >nul 2>&1
echo   [+] Removendo caches e temporarios (__pycache__)...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.spec >nul 2>&1
echo   [OK] Limpeza profunda concluida.
echo   [!] Lembre-se de reconfigurar o ambiente antes de iniciar o sistema novamente.
pause
goto MENU

:CLEAN_LICENSE
cls
echo.
echo   [!] LIMPANDO LICENCAS PARA SIMULAR NOVO CLIENTE...
echo.
if exist "LICENSA\license.key" (
    del /q "LICENSA\license.key"
    echo   [OK] Licenca local deletada.
)
if exist "%LOCALAPPDATA%\JUVICKS_DATA\LICENSA\license.key" (
    del /q "%LOCALAPPDATA%\JUVICKS_DATA\LICENSA\license.key"
    echo   [OK] Licenca instalada deletada.
)
echo.
echo   [RESULTADO] O sistema pedira uma nova chave no proximo inicio.
pause
goto MENU

:NO_VENV
echo.
echo   [ERRO] Pasta 'venv' nao localizada.
echo   Caminho esperado: %BASE_DIR%venv
echo   Recomendado: Use a opcao [9] para reinstalar.
pause
goto MENU

:NO_SCRIPT
echo.
echo   [ERRO] Arquivo compilar.py ausente.
pause
goto MENU

:LANCHAR_GUI
start "" "PAINEL DE CONTROLE.bat" GUI
goto MENU
