@echo off
setlocal enabledelayedexpansion
color 0C
cls

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         JUVIKS HERO 07 - RESET MASTER DO SISTEMA         ║
echo  ║                  ⚠  ZONA DE PERIGO  ⚠                   ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  ATENCAO: Esta acao e IRREVERSIVEL!
echo  Os seguintes dados serao PERMANENTEMENTE APAGADOS:
echo.
echo   [•] Banco de dados principal (Clientes, Produtos, Orcamentos, Contratos)
echo   [•] Banco de assinaturas digitais e historico
echo   [•] Configuracoes e Sessao do WhatsApp (QR Code sera resetado)
echo   [•] Banco de orcamentos aprovados
echo   [•] Chave de licenca de ativacao
echo   [•] Cache e arquivos temporarios (__pycache__)
echo   [•] Logs de erro
echo.
echo  ============================================================
echo.

set /p confirma1="  Tem certeza? Digite SIM para continuar: "
if /i "!confirma1!" neq "SIM" (
    echo.
    echo  [CANCELADO] Nenhum dado foi apagado. Sistema intacto.
    pause
    exit /b
)

echo.
set /p confirma2="  ULTIMA CHANCE! Confirme novamente digitando ZERAR: "
if /i "!confirma2!" neq "ZERAR" (
    echo.
    echo  [CANCELADO] Nenhum dado foi apagado. Sistema intacto.
    pause
    exit /b
)

echo.
echo  [+] Encerrando todos os processos do sistema...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM streamlit.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1
timeout /t 2 >nul

SET "BASE=%~dp0..\"

echo  [+] Apagando banco de dados principal (Clientes/Vendas)...
if exist "%BASE%DATABASE\sistema_vendas.db" (
    del /f /q "%BASE%DATABASE\sistema_vendas.db"
    echo      [OK] sistema_vendas.db removido.
)

echo  [+] Apagando banco de assinaturas digitais...
if exist "%BASE%PY\assiname_app\assinaturas.db" (
    del /f /q "%BASE%PY\assiname_app\assinaturas.db"
    echo      [OK] assinaturas.db removido.
)

echo  [+] Resetando conexao do WhatsApp (Sessao)...
if exist "%BASE%PY\WHATSAPP_MOTOR\.wwebjs_auth" (
    rd /s /q "%BASE%PY\WHATSAPP_MOTOR\.wwebjs_auth"
    echo      [OK] Sessao do WhatsApp removida.
)

echo  [+] Apagando banco de orcamentos aprovados...
if exist "%BASE%DATABASE\orcamentos_aprovados.db" (
    del /f /q "%BASE%DATABASE\orcamentos_aprovados.db"
    echo      [OK] orcamentos_aprovados.db removido.
)

echo  [+] Apagando chave de licenca...
if exist "%BASE%LICENSA\license.key" (
    del /f /q "%BASE%LICENSA\license.key"
    echo      [OK] license.key removida.
)

echo  [+] Apagando logs de erro...
if exist "%BASE%LOG_DB.txt" (
    del /f /q "%BASE%LOG_DB.txt"
    echo      [OK] LOG_DB.txt removido.
)

echo  [+] Limpando cache Python (__pycache__)...
for /d /r "%BASE%" %%d in (__pycache__) do (
    if exist "%%d" (
        rd /s /q "%%d" >nul 2>&1
    )
)
echo      [OK] Cache limpo.

echo  [+] Apagando arquivos .pyc...
del /s /q "%BASE%*.pyc" >nul 2>&1
echo      [OK] Arquivos .pyc removidos.

echo.
echo  ============================================================
echo.
echo  ✔ RESET COMPLETO EFETUADO COM SUCESSO!
echo.
echo  O sistema voltou ao estado de fabrica.
echo  Na proxima inicializacao ele pedira:
echo    → Uma nova Chave de Licenca
echo    → Novo QR Code do WhatsApp
echo    → Cadastro de empresa e configuracoes iniciais
echo.
echo  ============================================================
echo.
pause
