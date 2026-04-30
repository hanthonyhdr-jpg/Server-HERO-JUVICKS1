@echo off
title RESETAR SISTEMA
color 4F

echo =========================================================
echo                  AVISO DE SEGURANCA
echo =========================================================
echo.
echo Voce esta prestes a RESETAR O SISTEMA completamente.
echo Isso ira apagar TODOS os seus dados, incluindo:
echo.
echo  - Clientes e Orcamentos
echo  - Todas as Configuracoes
echo  - Todos os Usuarios e Senhas (Voltara para admin/123)
echo  - Historico de Acessos
echo.
echo ESTA ACAO NAO PODE SER DESFEITA!
echo.
set /p confirma="Digite 'SIM' para apagar tudo ou feche esta janela para cancelar: "

if /I "%confirma%" NEQ "SIM" (
    echo.
    echo Operacao cancelada! Nenhum dado foi apagado.
    pause
    exit
)

echo.
echo Apagando banco de dados...
del /q /f "%~dp0DATABASE\sistema_vendas.db" 2>nul

echo Limpando sessoes salvas...
del /q /f "%~dp0PY\login_auto.txt" 2>nul
del /q /f "%~dp0login_auto.txt" 2>nul

echo.
echo.
echo =========================================================
echo         SISTEMA RESETADO COM SUCESSO!
echo =========================================================
echo.
echo Ao abrir o sistema novamente, as configuracoes padroes
echo e o usuario 'admin' (com a senha padrao escolhida) 
echo serao recriados automaticamente.
echo.
pause
