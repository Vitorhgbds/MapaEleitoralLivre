# -*- mode: python ; coding: utf-8 -*-
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Assuming the .spec file is in the root of your Django project
project_root = os.path.abspath('.')

datas = [
    (os.path.join(project_root, 'MEL/templates'), 'MEL/templates'),
    (os.path.join(project_root, 'MEL/static'), 'MEL/static'),
    # Add other directories as needed
]

a = Analysis(['manage.py'],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
coll = COLLECT(exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='mel',
)
