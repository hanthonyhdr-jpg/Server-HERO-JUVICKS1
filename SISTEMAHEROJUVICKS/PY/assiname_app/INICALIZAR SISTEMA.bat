@echo off
title Sistema Assinatura Digital - Antigravity
echo ========================================================
echo        SISTEMA DE ASSINATURA DIGITAL (STYLE AUTHENTIQUE)
echo ========================================================
echo.

:: Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH. Por favor, instale o Python.
    pause
    exit /b
)

:: Criar ambiente virtual se nao existir (opcional mas recomendado)
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
)

:: Ativar ambiente virtual
call venv\Scripts\activate

:: Instalar dependencias
echo [INFO] Instalando/Atualizando dependencias (isso pode levar um minuto na primeira vez)...
pip install -r requirements.txt --quiet

:: Avisar sobre o Ngrok
echo.
echo ========================================================
echo [LEMBRETE] Para o cliente acessar, voce deve rodar em OUTRO terminal:
echo           ngrok http 5000
echo ========================================================
echo.

:: Iniciar aplicacao
echo [INFO] Iniciando servidor Flask em http://127.0.0.1:5000
python app.py

pause
