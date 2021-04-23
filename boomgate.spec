# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['boomgate.py', 'scripts/camera_stream.py', 'scripts/boomgate_gui.py', 'scripts/form.py', 'image/image_loader.py'],
             pathex=['C:\\wsl\\dev\\python-oop\\testing\\_docker\\_boomgate'],
             binaries=[],
             datas=[('ui/icon/black-icon.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='boomgate',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='ui\\icon\\black-icon.ico')
