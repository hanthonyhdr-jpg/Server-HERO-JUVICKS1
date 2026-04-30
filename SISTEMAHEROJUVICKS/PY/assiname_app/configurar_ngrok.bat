@echo off
title Configurar Token Ngrok - Assinatura Digital
echo ========================================================
echo        CONFIGURACAO DE AUTENTICACAO DO NGROK
echo ========================================================
echo.
echo Para o Ngrok funcionar sem limites e com HTTPS, voce precisa de um Token.
echo.
echo 1. Va ate: https://dashboard.ngrok.com/get-started/your-authtoken
echo 2. Copie o seu "Your Authtoken"
echo.
set /p NGROK_TOKEN="Cole o seu Token aqui e aperte ENTER: "

if "%NGROK_TOKEN%"=="" (
    echo [ERRO] Token nao pode ser vazio!
    pause
    exit /b
)

echo.
echo [INFO] Configurando o Ngrok com o seu Token...
ngrok config add-authtoken %NGROK_TOKEN%

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Nao foi possivel configurar o token. 
    echo Verifique se o ngrok.exe esta instalado no seu PATH.
) else (
    echo.
    echo ========================================================
    echo [SUCESSO] Ngrok configurado com sucesso!
    echo Agora voce pode usar o 'start_ngrok.bat' para abrir o tunel.
    echo ========================================================
)

pause
