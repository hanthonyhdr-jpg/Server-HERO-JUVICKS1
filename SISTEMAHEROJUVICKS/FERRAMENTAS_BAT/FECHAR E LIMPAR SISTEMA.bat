@echo off
echo Encerrando processo SISTEMA_JUVIKS_OFICIAL.exe...
taskkill /F /IM "SISTEMA_JUVIKS_OFICIAL.exe"
if %ERRORLEVEL% == 0 (
    echo Processo encerrado com sucesso!
) else (
    echo Processo nao encontrado ou nao foi possivel encerrar.
)

echo.
echo Removendo pastas _MEI* do Temp...
for /d %%D in ("C:\Users\%USERNAME%\AppData\Local\Temp\_MEI*") do (
    echo Deletando: %%D
    rd /s /q "%%D"
)
echo Limpeza concluida!
pause