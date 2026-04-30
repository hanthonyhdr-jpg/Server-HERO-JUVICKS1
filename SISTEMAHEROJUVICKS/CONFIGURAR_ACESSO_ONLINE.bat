@echo off
title CONFIGURADOR DE ACESSO ONLINE - JUVICKS HERO
mode con: cols=80 lines=25
color 0b

:: Verifica se o ngrok.exe existe na pasta atual ou onde o sistema está
set "NGROK_EXE=ngrok.exe"
if not exist "%NGROK_EXE%" (
    if exist "PY\ngrok.exe" set "NGROK_EXE=PY\ngrok.exe"
)

:MENU
cls
echo ==============================================================
echo           CONFIGURADOR DE ACESSO ONLINE - NGROK
echo ==============================================================
echo.
echo [1] CONFIGURAR NOVO TOKEN (Authtoken)
echo [2] CONFIGURAR NOVO DOMINIO FIXO (Link Estatico)
echo [3] LIMPAR CONFIGURACOES ANTIGAS (Resetar Tudo)
echo [4] SAIR
echo.
set /p op="Escolha uma opcao: "

if "%op%"=="1" goto TOKEN
if "%op%"=="2" goto DOMINIO
if "%op%"=="3" goto RESET
if "%op%"=="4" exit

:TOKEN
cls
echo ==============================================================
echo           CONFIGURACAO DE AUTHTOKEN (TOKEN)
echo ==============================================================
echo.
echo Para pegar seu token, acesse: https://dashboard.ngrok.com/
echo.
set /p token="Cole seu Authtoken aqui e de Enter: "
if "%token%"=="" goto MENU

echo.
echo [+] Salvando novo Token...
"%NGROK_EXE%" config add-authtoken %token%
echo.
echo [OK] Token configurado com sucesso!
pause
goto MENU

:DOMINIO
cls
echo ==============================================================
echo           CONFIGURACAO DE DOMINIO FIXO (LINK)
echo ==============================================================
echo.
echo Exemplo: seu-sistema.ngrok-free.app
echo.
set /p domain="Digite seu novo Dominio aqui: "
if "%domain%"=="" goto MENU

echo %domain%> ngrok_dominio.txt
echo.
echo [OK] Arquivo 'ngrok_dominio.txt' atualizado com sucesso!
echo Link atual: https://%domain%
pause
goto MENU

:RESET
cls
echo ==============================================================
echo           LIMPEZA DE CONFIGURACOES
echo ==============================================================
echo.
echo [+] Removendo arquivos temporarios do Ngrok...
if exist "%LOCALAPPDATA%\ngrok\ngrok.yml" (
    del /f /q "%LOCALAPPDATA%\ngrok\ngrok.yml"
    echo [OK] Arquivo yml removido do sistema.
)
if exist "ngrok_dominio.txt" (
    del /f /q "ngrok_dominio.txt"
    echo [OK] Arquivo de dominio local removido.
)
echo.
echo [+] Reiniciando processos ativos...
taskkill /f /im ngrok.exe >nul 2>&1
echo.
echo [OK] Sistema limpo.
pause
goto MENU
