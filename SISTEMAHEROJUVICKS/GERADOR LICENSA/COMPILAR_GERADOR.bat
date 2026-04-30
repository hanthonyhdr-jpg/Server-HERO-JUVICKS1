@echo off
title COMPILADOR DE GERADOR DE LICENCAS - JUVIKS
color 0E
cls

:: Define diretorio base
SET "BASE_DIR=%~dp0"
CD /D "%BASE_DIR%"

echo ==============================================================
echo       CONVERSOR DE PYTHON PARA EXE (GERADOR DE LICENCAS)
echo ==============================================================
echo.

:: Detectar se o Python esta no PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no Windows.
    pause
    exit
)

echo [+] Instalando/Atualizando PyInstaller...
python -m pip install pyinstaller --quiet

echo.
echo [+] Iniciando a compilacao (Transformando .py em .exe)...
echo [+] A pasta \dist sera criada aqui dentro.
echo.

:: Limpeza de builds antigos
if exist "build" rd /s /q "build"
if exist "*.spec" del /q "*.spec"

:: Compila sem icone customizado (usara o padrao do Python/PyInstaller)
pyinstaller --noconfirm --onefile --console ^
    --name "GERADOR_DE_CHAVES_JUVIKS" ^
    "gerador_licenca.py"

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao gerar o executavel. 
) else (
    echo.
    echo ==============================================================
    echo [OK] SUCESSO! O executavel foi gerado na pasta \dist.
    echo [OK] Local: %CD%\dist\GERADOR_DE_CHAVES_JUVIKS.exe
    echo ==============================================================
    
    :: Opcional: Abre a pasta dist para o usuario
    start explorer "%CD%\dist"
)

echo.
pause
exit
