@echo off
color 04
title [JUVIKS] MODO HACKER / RESET MASTER
echo ========================================================
echo          RECUPERACAO ABSOLUTA DE ACESSOS JUVIKS
echo ========================================================
echo.
echo [ATENCAO] Esta ferramenta ira destruir logins anteriores 
echo e forcar o seu PC atual a aceitar voce como Dono (Master).
echo.

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERRO] O Ambiente VENV nao foi iniciado! Voce deve "Reparar Ambiente" primeiro!
    pause
    exit /b
)

"%~dp0venv\Scripts\python.exe" "%~dp0FERRAMENTAS_BAT\resetar_acessos.py"

echo.
pause
