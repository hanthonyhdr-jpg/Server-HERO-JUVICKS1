@echo off
chcp 65001 >nul
color 0C
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║        JUVIKS SERVER - LIMPEZA DE SESSAO             ║
echo  ║   Remove login salvo, cache e registros de acesso    ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

set ROOT=%~dp0
set SESSIONS_DIR=%ROOT%PY\sessions
set LOCALAPP_DIR=%LOCALAPPDATA%\JUVICKS_DATA\sessions

echo  [1/4] Removendo arquivo de sessao do servidor...
if exist "%SESSIONS_DIR%\last_session.json" (
    del /f /q "%SESSIONS_DIR%\last_session.json"
    echo      [OK] last_session.json removido.
) else (
    echo      [--] Nenhuma sessao de servidor encontrada.
)

echo.
echo  [2/4] Removendo sessao do AppData (instalacao em Program Files)...
if exist "%LOCALAPP_DIR%\last_session.json" (
    del /f /q "%LOCALAPP_DIR%\last_session.json"
    echo      [OK] Sessao AppData removida.
) else (
    echo      [--] Nenhuma sessao AppData encontrada.
)

echo.
echo  [3/4] Removendo sessoes ativas do banco de dados local...
set SQLITE_DB=%ROOT%DATABASE\sistema.db
if exist "%SQLITE_DB%" (
    echo      Limpando tabela sessoes_ativas...
    sqlite3 "%SQLITE_DB%" "DELETE FROM sessoes_ativas;" 2>nul
    if %errorlevel% == 0 (
        echo      [OK] Tabela sessoes_ativas limpa.
    ) else (
        echo      [AVISO] sqlite3 nao encontrado no PATH. Pulando limpeza do banco.
    )
) else (
    echo      [--] Banco de dados nao encontrado localmente.
)

echo.
echo  [4/4] Limpando LocalStorage do navegador (login salvo)...
:: Cria uma pagina HTML temporaria que limpa o localStorage e fecha
set TEMP_HTML=%TEMP%\juviks_clear_cache.html
(
echo ^<!DOCTYPE html^>
echo ^<html^>^<head^>^<meta charset="UTF-8"^>
echo ^<title^>Limpando Juviks...^</title^>
echo ^<style^>body{background:#020b18;color:#00d4ff;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;flex-direction:column;gap:16px;}
echo .msg{font-size:18px;letter-spacing:2px;} .ok{color:#00ffcc;font-size:14px;}^</style^>
echo ^</head^>^<body^>
echo ^<div class="msg"^>⚡ JUVIKS - Limpando dados de acesso...^</div^>
echo ^<div class="ok" id="status"^>Aguarde...^</div^>
echo ^<script^>
echo try {
echo   localStorage.removeItem('juv_profiles');
echo   localStorage.removeItem('juv_last_user');
echo   // Limpa todos os cookies do dominio
echo   document.cookie.split(";").forEach(function(c) {
echo     document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
echo   });
echo   document.getElementById('status').textContent = '[OK] Cache de login removido com sucesso! Pode fechar esta aba.';
echo   document.getElementById('status').style.color = '#00ffcc';
echo } catch(e) {
echo   document.getElementById('status').textContent = 'Erro: ' + e.message;
echo   document.getElementById('status').style.color = '#ff4444';
echo }
echo ^</script^>
echo ^</body^>^</html^>
) > "%TEMP_HTML%"

start "" "%TEMP_HTML%"
echo      [OK] Pagina de limpeza aberta no navegador padrao.
echo           Aguarde 3 segundos e feche a aba.

echo.
echo  ══════════════════════════════════════════════════════
echo   LIMPEZA CONCLUIDA! 
echo   Proximo acesso ao sistema exigira login novamente.
echo  ══════════════════════════════════════════════════════
echo.
pause
