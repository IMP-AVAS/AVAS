# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
['main.py', ],
    pathex=[r'F:\AVAS_CONTROL\AVAS\AVAS'],
    binaries=[],
    datas=[('./dllfile/AVAS.dll', 'dllfile'),
    ('./dllfile/AVAS.lib', 'dllfile'),
    ('./dllfile/libfftw3-3.dll', 'dllfile'),
    ('./dllfile/libfftw3f-3.dll', 'dllfile'),
    ('./dllfile/libfftw3l-3.dll', 'dllfile'),
    ('./dllfile/MSVCP140.dll', 'dllfile'),
    ('./dllfile/LinacMTLIB.dll', 'dllfile'),
    ('./dllfile/LongAccelerator2.dll', 'dllfile'),
    ('./dllfile/LongAccelerator3.dll', 'dllfile'),

    ('./staticfile/ifr.txt','staticfile'),
    ('./staticfile/ifx3d_3.txt','staticfile'),
    ('./staticfile/ifz.txt','staticfile'),
    ('./staticfile/ifz3d_3.txt','staticfile'),

    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='AVAS',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AVAS',
)