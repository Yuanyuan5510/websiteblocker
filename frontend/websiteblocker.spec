# -*- mode: python ; coding: utf-8 -*-

import sys

block_cipher = None

# 图标文件路径
icon_path = r'j:\pyiadea312\限制网站访问\4.4\browser\app_icon.png'

# 版本信息文件路径
version_info_path = 'version_info.txt'

# 应用程序信息
author = 'wang.station'
publisher = 'wang.station'
support_email = 'wang.station@hotmail.com'
support_url = 'websiteblocker-zh.wangstation.ddns-ip.net'

# 主脚本分析
a = Analysis(
    ['server.js'],
    pathex=[],
    binaries=[],
    datas=[
        ('dist', 'dist')
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

# 生成可执行文件配置
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

executables = [
    EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='websiteblocker',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,  # 不显示终端窗口
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,  # 指定图标文件
        version_file=version_info_path,  # 添加版本信息文件引用
        onefile=True,  # 生成单文件EXE
    )
]

# 移除COLLECT部分，因为使用onefile=True
# a_col = COLLECT(
#     executables,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='websiteblocker',
# )
