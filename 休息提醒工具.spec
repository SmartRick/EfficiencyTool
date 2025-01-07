# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

datas = [('src/config/style.yaml', 'src/config'), ('src/assets', 'src/assets'), ('README.md', '.')]
hiddenimports = []
datas += collect_data_files('PySide6')
hiddenimports += collect_submodules('PySide6')


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'email', 'html', 'http', 'xml', 'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile', 'pickle', 'calendar', 'numpy.random', 'numpy.core', 'numpy.testing', 'scipy', 'pandas', 'matplotlib', 'cryptography', 'PIL', 'pytz', 'setuptools', 'pkg_resources'],
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
    name='休息提醒工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime140.dll', 'Qt*.dll', 'PySide6*.dll'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src\\assets\\app.ico'],
)
