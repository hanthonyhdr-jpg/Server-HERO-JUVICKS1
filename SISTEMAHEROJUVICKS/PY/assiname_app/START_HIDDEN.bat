@echo off
title ASSINA HD - GERENCIADOR
echo [INFO] Iniciando Sistema em Segundo Plano...
echo [AVISO] O console sera fechado e o sistema ficara oculto no Tray (perto do relogio).

:: Instalar pystray se nao existir
pip install pystray Pillow --quiet

:: Iniciar o tray em modo bypass do console (pythonw)
start /b pythonw main_tray.py

echo [SUCESSO] Sistema Iniciado! Procure o icone azul na Barra de Tarefas (System Tray).
exit
