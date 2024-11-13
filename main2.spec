# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],

    datas=[
    ('robotouille', 'robotouille'), 
    ('backend', 'backend')],
    hiddenimports=['robotouille', 'robotouille.env', 'robotouille.robotouille_env', 'robotouille.robotouille_simulator'],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    onefile=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/path/to/icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
