# -*- mode: python ; coding: utf-8 -*-
"""
Fichier spec pour PyInstaller - Pokemon Dataset Generator
Pour utiliser : pyinstaller pokemon_dataset_generator.spec
"""

block_cipher = None

a = Analysis(
    ['GUI_v2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('cards_info.xlsx', '.'),
        ('gui_config.json', '.') if os.path.exists('gui_config.json') else None,
    ],
    hiddenimports=[
        'cv2',
        'pandas',
        'numpy',
        'imgaug',
        'PIL',
        'openpyxl',
        'tkinter',
        'scipy',
        'scikit-image',
        'imagecorruptions',
    ],
    hookspath=[],
    hooksconfig={},
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Pokemon_Dataset_Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Ajoutez un chemin vers un .ico si vous en avez un
)
