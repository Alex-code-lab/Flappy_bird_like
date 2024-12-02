# -*- mode: python ; coding: utf-8 -*-
# Spécifie que le fichier est un script Python et utilise l'encodage UTF-8.
# Cela garantit que les caractères spéciaux sont correctement interprétés.

a = Analysis(
    ['main.py'],                # Le script principal de votre application, à analyser pour inclure ses dépendances.
    pathex=[],                  # Chemins supplémentaires où chercher des modules ou fichiers. Vide ici.
    binaries=[],                # Liste de fichiers binaires à inclure. Aucun binaire spécifique n'est ajouté.
    datas=[('resources', 'resources')],  # Inclut tout le contenu du dossier "resources". Cela permet de l'utiliser dans l'exécutable final.
    hiddenimports=[],           # Liste des modules que PyInstaller n'a pas détectés automatiquement. Vide ici.
    hookspath=[],               # Chemins vers des scripts de hooks personnalisés. Aucun n'est utilisé.
    hooksconfig={},             # Configuration des hooks. Aucun paramètre personnalisé ici.
    runtime_hooks=[],           # Scripts Python exécutés avant le lancement de l'application. Aucun ici.
    excludes=[],                # Modules explicitement exclus. Vide ici.
    noarchive=False,            # Si `True`, les fichiers Python sont extraits au lieu d'être inclus dans l'archive. Ici, `False` (inclus dans l'archive).
    optimize=0,                 # Niveau d'optimisation Python (0 = aucune optimisation, 1 ou 2 = optimisé). Ici, pas d'optimisation.
)
# Cette section configure l'analyse initiale de votre script. Elle identifie les fichiers nécessaires.

pyz = PYZ(a.pure)
# Génère un fichier PYZ qui regroupe les fichiers Python "purs" (sans dépendances natives).

exe = EXE(
    pyz,                        # Le fichier PYZ précédemment généré.
    a.scripts,                  # Les scripts analysés lors de l'étape d'Analysis.
    a.binaries,                 # Les fichiers binaires identifiés.
    a.datas,                    # Les fichiers de données inclus.
    [],                         # Fichiers supplémentaires spécifiques à l'EXE. Aucun ici.
    name='JoyeuxAnniversaire',  # Nom de l'exécutable généré.
    debug=False,                # Si `True`, l'exécutable inclut des informations de débogage.
    bootloader_ignore_signals=False,  # Si `True`, ignore certains signaux système dans le bootloader.
    strip=False,                # Si `True`, supprime les symboles de débogage des binaires (non activé ici).
    upx=True,                   # Si `True`, compresse les binaires avec UPX.
    upx_exclude=[],             # Liste des fichiers exclus de la compression UPX.
    runtime_tmpdir=None,        # Répertoire temporaire pour extraire les fichiers au runtime. `None` utilise un répertoire par défaut.
    console=False,              # Si `True`, affiche une console (fenêtre de terminal). Ici, désactivé.
    disable_windowed_traceback=False,  # Si `True`, désactive l'affichage des exceptions sous forme de fenêtre.
    argv_emulation=False,       # Permet l'émulation des arguments de la ligne de commande sur macOS. Désactivé ici.
    target_arch=None,           # Architecture cible (32 bits ou 64 bits). `None` détecte automatiquement.
    codesign_identity=None,     # Identité de signature de code (nécessaire pour distribuer sous macOS). `None` ici.
    entitlements_file=None,     # Fichier d'entitlements (permissions spécifiques pour macOS). Aucun ici.
    icon='resources/app_icon.icns',  # Icône de l'application au format .icns (spécifique à macOS).
)
# Cette section configure les paramètres de l'exécutable final.

app = BUNDLE(
    exe,                        # L'exécutable généré dans la section précédente.
    name='JoyeuxAnniversaire.app',  # Nom du bundle macOS (le fichier .app final).
    icon='resources/app_icon.icns', # Icône utilisée pour le bundle.
    bundle_identifier=None,     # Identifiant unique pour le bundle (exemple : com.monde.nomDuProjet). `None` ici.
)
# Cette section crée un bundle spécifique pour macOS (.app).