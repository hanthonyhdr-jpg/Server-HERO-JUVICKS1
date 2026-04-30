# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Aumenta o limite de recursão para evitar erros com Streamlit
sys.setrecursionlimit(2000)

block_cipher = None

ROOT = os.path.abspath('.')

# Caminho do projeto
ROOT = os.path.abspath('.')

from PyInstaller.utils.hooks import collect_all

# Coletando tudo do streamlit e componentes para evitar erro de diretório ausente
# Coleta otimizada de dependências (evitando duplicidade de páginas)
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

st_datas, st_binaries, st_hiddenimports = collect_all('streamlit')

canvas_datas = collect_data_files('streamlit_drawable_canvas')
canvas_binaries = collect_dynamic_libs('streamlit_drawable_canvas')
canvas_hiddenimports = collect_submodules('streamlit_drawable_canvas')

pa_datas = collect_data_files('pyarrow')
pa_binaries = collect_dynamic_libs('pyarrow')
pa_hiddenimports = collect_submodules('pyarrow')

pd_datas = collect_data_files('pandas')
pd_binaries = collect_dynamic_libs('pandas')
pd_hiddenimports = collect_submodules('pandas')

pl_datas = collect_data_files('plotly')
pl_binaries = collect_dynamic_libs('plotly')
pl_hiddenimports = collect_submodules('plotly')

al_datas, al_binaries, al_hiddenimports = collect_all('altair')

pil_datas, pil_binaries, pil_hiddenimports = collect_all('PIL')

a = Analysis(
    ['PY/launcher.py'],
    pathex=[ROOT],
    binaries=st_binaries + canvas_binaries + pa_binaries + pd_binaries + pl_binaries + al_binaries + pil_binaries,
    datas=[
        (os.path.join(ROOT, 'PY'), 'PY'),
        (os.path.join(ROOT, 'ICONE'), 'ICONE'),
        (os.path.join(ROOT, 'MODELOS_HTML'), 'MODELOS_HTML'),
        (os.path.join(ROOT, 'TELA'), 'TELA'),
        (os.path.join(ROOT, 'CONFIG_SISTEMA'), 'CONFIG_SISTEMA'),
        (os.path.join(ROOT, 'DATABASE'), 'DATABASE'),
        (os.path.join(ROOT, 'assiname_app'), 'assiname_app'),
        (os.path.join(ROOT, 'ngrok.exe'), '.'),
    ] + st_datas + canvas_datas + pa_datas + pd_datas + pl_datas + al_datas + pil_datas,
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'fpdf',
        'docx2pdf',
        'pywin32',
        'requests',
        'xlsxwriter',
        'pillow',
        'pystray',
        'openpyxl',
        'flask',
        'werkzeug',
        'fitz',
        'streamlit_drawable_canvas',
        'numpy',
        'watchdog',
        'altair',
        'sqlite3',
        'multiprocessing',
        'ctypes',
        'webbrowser',
        'threading',
        'time',
        'psycopg2', # Importante para o banco
        'urllib.request',
        'psutil', # Necessário para desligamento inteligente
        'docx', # Para geração de contratos (python-docx)
        'pythoncom',
        'win32com.client',
        'pyarrow',
        'pydoc',
        'pydoc_data',
        'pydoc_data.topics',
        'assiname_app',
        'assiname_app.app'
    ] + st_hiddenimports + canvas_hiddenimports + pa_hiddenimports + pd_hiddenimports + pl_hiddenimports + al_hiddenimports + pil_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 
        'notebook', 
        'IPython', 
        'jedi', 
        'test', 
        'unittest',
        'lib2to3', 
        'git', 
        'sqlite3.test', 
        'numpy.tests',
        'tqdm',
        'IPython.core',
        'pydeck'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HERO_JUVICKS_SERVER_10',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, 'ICONE', 'ICONE.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HERO_JUVICKS_SERVER_10',
)

