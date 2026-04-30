@echo off
title Instalador de Dependencias e Ngrok - Assinatura Digital
echo ========================================================
echo        INSTALADOR E CONFIGURADOR (STYLE AUTHENTIQUE)
echo ========================================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Por favor, instale o Python.
    pause
    exit /b
)

:: 2. Criar ambiente virtual e instalar dependencias
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
)
echo [INFO] Ativando ambiente virtual e instalando requisitos...
call venv\Scripts\activate
pip install -r requirements.txt --quiet

:: 3. Baixar Ngrok se nao existir
if not exist "ngrok.exe" (
    echo [INFO] Baixando Ngrok para a pasta local...
    :: Usando PowerShell para baixar o zip oficial do Ngrok para Windows x64
    powershell -Command "& {Invoke-WebRequest -Uri 'https://bin.equinox.io/c/b34edq6L9Xt/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'}"
    
    if exist "ngrok.zip" (
        echo [INFO] Extraindo ngrok.exe...
        powershell -Command "& {Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force}"
        del ngrok.zip
        echo [SUCESSO] Ngrok baixado e extraído.
    ) else (
        echo [AVISO] Nao foi possivel baixar o Ngrok automaticamente.
        echo Por favor, coloque o ngrok.exe manualmente nesta pasta.
    )
) else (
    echo [INFO] Ngrok ja existe na pasta.
)

echo.
echo ========================================================
echo [CONCLUIDO] Dependencias instaladas e Ngrok pronto.
echo.
echo Agora voce deve:
echo 1. Rodar 'configurar_ngrok.bat' (apenas na primeira vez)
echo 2. Rodar 'start.bat' para iniciar o sistema
echo ========================================================
pause
