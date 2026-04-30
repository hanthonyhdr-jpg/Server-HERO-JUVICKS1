@echo off
title FINALIZADOR JUVIX HERO
echo ======================================================
echo           FINALIZANDO SISTEMA JUVIX HERO
echo ======================================================
echo.

echo [+] Finalizando Motor do WhatsApp (Node.js)...
taskkill /F /IM node.exe /T >nul 2>&1

echo [+] Finalizando Chrome/Driver (Automacao)...
taskkill /F /IM chromedriver.exe >nul 2>&1
taskkill /F /IM chrome.exe >nul 2>&1

echo [+] Finalizando Sistema Principal (Python/Streamlit)...
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo.
echo ======================================================
echo           SISTEMA FINALIZADO COM SUCESSO!
echo ======================================================
echo.
pause
