@echo off
title Editor de Tema — JUVIKS07
echo.
echo  ========================================
echo   Editor de Tema Visual JUVIKS07
echo  ========================================
echo.

:: Garante que o diretório de trabalho é a pasta do .bat
cd /d "%~dp0"

:: Caminho absoluto para o Python do venv do projeto
set PYTHON_EXE=%~dp0..\venv\Scripts\python.exe

if exist "%PYTHON_EXE%" (
    echo  Usando Python do venv: %PYTHON_EXE%
    echo  Aguarde o navegador abrir em http://localhost:8599
    echo.
    "%PYTHON_EXE%" -m streamlit run editor_tema.py --server.port=8599 --server.headless=false
) else (
    echo  venv nao encontrado, tentando Python global...
    python -m streamlit run editor_tema.py --server.port=8599 --server.headless=false
)

pause
