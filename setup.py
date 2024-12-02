from setuptools import setup
import sys

sys.setrecursionlimit(5000)

data_files = [
    ('resources', [
        'resources/app_icon.icns',  # Vous pouvez ajouter une icône si nécessaire
    ]),
]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame'],
    'resources': ['resources/'],
    'iconfile': 'resources/app_icon.icns',
    'plist': {
        'CFBundleName': 'TestMinimal',
        'CFBundleDisplayName': 'Test Minimal',
        'CFBundleIdentifier': 'com.votreentreprise.testminimal',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=['main.py'],
    data_files=data_files,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)