@echo off
title MOTOR WHATSAPP JUVIX
echo ======================================================
echo          INICIANDO MOTOR DE ENVIO (NODE.JS)
echo ======================================================
echo.

:: Corrigido o caminho para entrar na pasta PY primeiro
cd /d "%~dp0PY\WHATSAPP_MOTOR"
if exist gateway.js (
    echo [+] Iniciando Gateway em %cd%...
    node gateway.js
) else (
    echo [!] ERRO: Arquivo gateway.js nao encontrado em PY\WHATSAPP_MOTOR.
    echo Caminho atual: %cd%
)

echo.
pause
