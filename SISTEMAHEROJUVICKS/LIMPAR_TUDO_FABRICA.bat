@echo off
setlocal
title LIMPANDO SISTEMA JUVIKS PARA PRODUCAO...
color 0C

echo ==============================================================
echo ATENCAO: AREA DE PERIGO - RESET DE FABRICA
echo ==============================================================
echo.
echo ESTA ACAO IRA APAGAR TODOS OS REGISTROS DO BANCO DE DADOS:
echo - Clientes, Orcamentos, Contratos
echo - Lancamentos Financeiros, Agenda, Logs de Acesso
echo - Configuracoes de Empresa, Motor WhatsApp e Assinaturas
echo - Todos os Usuarios e Chaves (exceto o Administrador padrao)
echo.
echo O SISTEMA FICARA COMPLETAMENTE LIMPO PARA EMPACOTAR A NOVA VERSAO.
echo.
echo Pressione CTRL+C para CANCELAR ou
pause

echo.
echo Iniciando limpeza profunda (PostgreSQL e SQLite)...
python PY\reset_fabrica.py

echo.
echo Limpeza Concluida! O banco esta zerado.
echo Ao rodar o sistema novamente, as chaves e admin iniciais serao regerados.
echo Pressione qualquer tecla para finalizar.
pause >nul
