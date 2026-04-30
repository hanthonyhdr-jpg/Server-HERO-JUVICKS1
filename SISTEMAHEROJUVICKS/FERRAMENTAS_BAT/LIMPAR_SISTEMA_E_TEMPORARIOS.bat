@echo off
setlocal
color 0C
title LIMPEZA DE EMERGENCIA - JUVIKS HERO

echo ================================================================
echo             LIMPANDO PROCESSOS E ARQUIVOS TEMPORARIOS
echo ================================================================
echo.

:: 1. FINALIZAR PROCESSOS
echo [+] Encerrando executaveis do sistema...
taskkill /F /IM "SISTEMA_JUVIKS_OFICIAL.exe" /T >nul 2>&1
taskkill /F /IM "SISTEMA.exe" /T >nul 2>&1
taskkill /F /IM "Inicio.exe" /T >nul 2>&1
taskkill /F /IM "launcher.exe" /T >nul 2>&1
taskkill /F /IM "python.exe" /T >nul 2>&1
taskkill /F /IM "pythonw.exe" /T >nul 2>&1
taskkill /F /IM "streamlit.exe" /T >nul 2>&1
timeout /t 2 >nul

:: 2. LIMPAR PASTA TEMP DO WINDOWS (PyInstaller _MEI)
echo [+] Localizando e removendo pastas temporarias (_MEI)...
cd /d %TEMP%
for /d %%i in (_MEI*) do (
    echo [LIMPANDO] %%i
    rd /s /q "%%i" >nul 2>&1
)

:: 3. LIMPAR CACHE DE SESSAO LOCAL (Se existir na pasta do sistema)
echo [+] Limpando cache do sistema...
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"
if exist "PY\__pycache__" rd /s /q "PY\__pycache__" >nul 2>&1
if exist "PY\pages\__pycache__" rd /s /q "PY\pages\__pycache__" >nul 2>&1
if exist "PY\utils\__pycache__" rd /s /q "PY\utils\__pycache__" >nul 2>&1

echo.
echo ================================================================
echo   LIMPEZA CONCLUIDA! O SISTEMA ESTA PRONTO PARA REINICIAR.
echo ================================================================
echo.
pause
exit
