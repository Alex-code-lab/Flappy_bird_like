import os
from PyInstaller.utils.hooks import get_module_file_attribute

# Only do this if PyQt5 is found.
mfi = get_module_file_attribute('PyQt5')
if mfi:
    # Determine the name of all these modules by looking in the PyQt5 directory.
    hiddenimports = []
    for f in os.listdir(os.path.dirname(mfi)):
        root, ext = os.path.splitext(os.path.basename(f))
        if root.startswith('Qt') and root != 'Qt':
            # On Linux and OS X, PyQt 5.14.1 has a `.abi3` suffix on all library names.
            if ext in ('.abi3.so', '.so', '.dll', '.pyd'):
                hiddenimports.append('PyQt5.' + root)