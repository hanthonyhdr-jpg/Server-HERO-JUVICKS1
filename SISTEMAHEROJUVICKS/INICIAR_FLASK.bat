@echo off
echo Iniciando Flask na porta 5001...
cd /d "%~dp0PY\assiname_app"
..\venv\Scripts\python.exe app.py --port 5001
pause