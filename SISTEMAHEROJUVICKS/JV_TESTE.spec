# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

sys.setrecursionlimit(2000)

streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all('streamlit')
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all('pandas')
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all('plotly')
streamlit_drawable_canvas_datas, streamlit_drawable_canvas_binaries, streamlit_drawable_canvas_hiddenimports = collect_all('streamlit-drawable-canvas')
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
altair_datas, altair_binaries, altair_hiddenimports = collect_all('altair')


a = Analysis(
    ['../../JUVIX SERVER OPERACIONAL VERSAO FINAL - bkp/SISTEMA LIMPO - ESTAVEL/PY/launcher.py'],
    pathex=[],
    binaries=[] + streamlit_binaries + pandas_binaries + plotly_binaries + streamlit_drawable_canvas_binaries + numpy_binaries + altair_binaries,
    datas=[
        ('../../JUVIX SERVER OPERACIONAL VERSAO FINAL - bkp/SISTEMA LIMPO - ESTAVEL', 'SISTEMA LIMPO - ESTAVEL')
    ] + streamlit_datas + pandas_datas + plotly_datas + streamlit_drawable_canvas_datas + numpy_datas + altair_datas,
    hiddenimports=[
        'fpdf',
        'python-docx',
        'docx2pdf',
        'pywin32',
        'requests',
        'xlsxwriter',
        'pillow',
        'pystray',
        'openpyxl',
        'Flask',
        'Werkzeug',
        'PyMuPDF',
        'urllib3',
        'pyinstaller',
        'watchdog',
        'charset-normalizer'
    ] + streamlit_hiddenimports + pandas_hiddenimports + plotly_hiddenimports + streamlit_drawable_canvas_hiddenimports + numpy_hiddenimports + altair_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'notebook',
        'IPython',
        'tqdm',
        'jedi',
        'test'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JV_TESTE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JV_TESTE',
)
