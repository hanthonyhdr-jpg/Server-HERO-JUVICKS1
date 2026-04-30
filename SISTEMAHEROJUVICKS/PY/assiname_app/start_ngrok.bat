@echo off
title Ngrok Tunelador - Assinatura Digital
echo ========================================================
echo               TUNELADOR NGROK PARA ASSINATURA
echo ========================================================
echo.

:: Verificar se o ngrok existe
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Ngrok nao encontrado. Por favor, instale o Ngrok no PATH
    echo Baixe em: https://ngrok.com/download
    pause
    exit /b
)

echo [INFO] Abrindo tunel para a porta 5001...
echo [INFO] Voce deve copiar o link "Forwarding" gerado abaixo (ex: https://xxxx.ngrok-free.app)
echo.

ngrok http 5001
pause
