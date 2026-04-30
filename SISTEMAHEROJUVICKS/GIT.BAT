@echo off
cls
setlocal enabledelayedexpansion

echo ======================================================
echo           ENVIO MANUAL PARA GITHUB (SEM ERROS)
echo ======================================================

:: 1. Define a Pasta
set /p "folder=1. COLE O CAMINHO DA PASTA (ou arraste aqui): "
set "folder=%folder:"=%"
cd /d "%folder%"

if %errorlevel% neq 0 (
    echo [ERRO] Pasta nao encontrada.
    pause
    exit /b
)

:: 2. Define o Link do Repositório
set /p "repo=2. COLE O LINK DO REPOSITORIO (.git): "

:: 3. Tratamento de Arquivos Gigantes (>100MB)
echo.
echo [AVISO] Arquivos maiores que 100MB causam erro no GitHub.
set /p "ignore=Deseja ignorar arquivos .exe e .pkg pesados? (S/N): "

if /i "%ignore%"=="S" (
    echo [INFO] Criando regra para ignorar arquivos pesados...
    echo *.exe > .gitignore
    echo *.pkg >> .gitignore
    echo dist/ >> .gitignore
    echo build/ >> .gitignore
)

:: 4. Configuração e Identidade
echo.
echo [INFO] Inicializando Git e Identidade...
rd /s /q .git >nul 2>&1
git init
git config user.email "usuario@exemplo.com"
git config user.name "Hanthony"

:: 5. Preparação e Envio
echo [INFO] Adicionando arquivos...
git add -A
git commit -m "Upload manual via script"
git branch -M main
git remote add origin %repo%

echo.
echo [INFO] Enviando para o GitHub...
echo (Se o upload demorar, e por causa do tamanho dos arquivos)
git push -u origin main --force

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O GitHub recusou o envio. 
    echo Verifique se voce digitou 'S' para ignorar os arquivos maiores que 100MB.
) else (
    echo.
    echo ======================================================
    echo           SUCESSO! TUDO FOI ENVIADO.
    echo ======================================================
)

pause