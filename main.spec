# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('robotouille', 'robotouille'),
     ('backend', 'backend'), ('utils', 'utils'),
     ('pddlgym/rendering/assets', 'pddlgym/rendering/assets'),
     ('pddlgym/rendering/assets/minecraft_agent.png', 'pddlgym/rendering/assets'),
     ('pddlgym/rendering/assets/minecraft_log.jpg', 'pddlgym/rendering/assets'),
     ('environments', 'environments'),
     ('renderer', 'renderer'),
     ('domain', 'domain'),
     ('assets', 'assets')],
    hiddenimports=['robotouille', 'robotouille.env', 'robotouille.robotouille_env', 'robotouille.robotouille_simulator', 'pygame', 'pddlgym', 'utils.pddlgym_utils', 'utils.pddlgym_interface', 'environments','itertools','os','shutil', 're','gym', 'scicfg','renderer','json'],
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
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon-windowed.icns'],
)
app = BUNDLE(
    exe,
    name='main.app',
    icon='icon-windowed.icns',
    bundle_identifier=None,
)
