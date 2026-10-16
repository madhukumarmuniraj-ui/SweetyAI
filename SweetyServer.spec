# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('app/legal/legal_playbook.json', 'app/legal'), ('app/data/semantic_graph.json', 'app/data')]
binaries = []
hiddenimports = ['gguf', 'faster_whisper']
datas += copy_metadata('gguf')
datas += copy_metadata('tokenizers')
datas += copy_metadata('safetensors')
datas += copy_metadata('huggingface-hub')
datas += copy_metadata('tqdm')
datas += copy_metadata('regex')
datas += copy_metadata('filelock')
hiddenimports += collect_submodules('chromadb')
tmp_ret = collect_all('imageio_ffmpeg')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SweetyServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SweetyServer',
)
