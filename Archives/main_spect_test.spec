# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # Le script principal
    pathex=['.'],  # Chemins supplémentaires à inclure
    binaries=[],
    datas=[('resources', 'resources')],  # Ajouter le dossier "resources"
    hiddenimports=[],  # Modules non détectés automatiquement par PyInstaller
    hookspath=['./hooks'],  # Répertoire contenant vos hooks personnalisés
    runtime_hooks=[],
    excludes=[],
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
    name='JoyeuxAnnivAnatole',  # Nom de l'application
    debug=True,  # Inclure les messages de debug
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Fenêtre graphique (sans console)
    disable_windowed_traceback=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JoyeuxAnnivAnatole',  # Dossier de sortie
)

app = BUNDLE(
    coll,
    name='JoyeuxAnnivAnatole.app',  # Nom du bundle macOS
    icon='resources/app_icon.icns',  # Icône de l'application
    bundle_identifier=None,  # Identifier du bundle (ajoutez si nécessaire)
    info_plist=None,
    argv_emulation=True,
    osx_arch=None,
)