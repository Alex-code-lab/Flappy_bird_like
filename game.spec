# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules  # Supprimé Tree
from pathlib import Path

# Déterminer le chemin absolu vers le répertoire contenant le fichier spec
spec_path = '/Users/souchaud/Documents/Autre/2024_11_26_anniv_anatole'
resources = os.path.join(spec_path, 'resources')

# # Collecte tous les modules nécessaires pour MoviePy
# hidden_imports = collect_submodules('moviepy')

# Inclure toutes les données nécessaires
datas = [
    (os.path.join(resources, 'SuperMario256.ttf'), 'resources'),
    (os.path.join(resources, 'mario_volant.png'), 'resources'),
    (os.path.join(resources, 'brique.png'), 'resources'),
    (os.path.join(resources, 'plante.png'), 'resources'),
    (os.path.join(resources, 'nuage.png'), 'resources'),
    (os.path.join(resources, 'carapace_rouge.png'), 'resources'),
    (os.path.join(resources, 'carapace_verte.png'), 'resources'),
    (os.path.join(resources, 'mission_joyeux_anniversaire.png'), 'resources'),
    (os.path.join(resources, 'Game_over.png'), 'resources'),
    (os.path.join(resources, 'mario_theme_song.mp3'), 'resources'),
    # (str(resources / 'test_video.avi'), 'resources'),
]

a = Analysis(
    ['main.py'],  # Nom de votre script principal
    pathex=[str(spec_path)],  # Ajouter le répertoire du projet
    datas=datas,
    # hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='JoyeuxAnniversaire',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mettre à True si vous voulez voir la console
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JoyeuxAnniversaire',
)