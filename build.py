import os
import sys
import shutil
import glob
import requests
import zipfile
from PyInstaller.__main__ import run


# 清理旧的构建文件
def clean_build():
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            os.remove(file)

# 主打包函数
def build():
    # 清理旧文件
    clean_build()

    
    # 定义需要排除的模块
    excludes = [
        'tkinter', 'unittest', 'email', 'html', 'http', 'xml',
        'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
        'pickle', 'calendar'
    ]
    
    # 添加一些其他可以安全排除的模块
    excludes.extend([
        'numpy.random', 'numpy.core', 'numpy.testing',  # numpy 相关
        'scipy', 'pandas', 'matplotlib',  # 其他大型库
        'cryptography', 'PIL',  # 其他可能的大型依赖
        'pytz', 'setuptools', 'pkg_resources',  # 其他不需要的模块
    ])
    
    # 定义需要包含的数据文件
    datas = [
        ('src/config/style.yaml', 'src/config'),
        ('src/assets', 'src/assets'),
        ('README.md', '.'),
    ]
    
    # 构建命令
    opts = [
        'src/main.py',  # 主程序入口
        '--name=休息提醒工具',  # 程序名称
        '--noconsole',  # 不显示控制台
        '--noconfirm',  # 不确认覆盖
        '--clean',  # 清理临时文件
        '--onefile',  # 单文件模式
        '--icon=src/assets/app.ico',  # 程序图标
        '--collect-submodules=PySide6',  # 收集 PySide6 子模块
        '--collect-data=PySide6',  # 收集 PySide6 数据文件
    ]

    upx_dir = 'tools/upx'
    # 添加 UPX 选项
    if upx_dir:
        opts.extend([
            '--upx-dir', upx_dir,
            '--upx-exclude', 'vcruntime140.dll',  # 排除特定文件
            '--upx-exclude', 'Qt*.dll',  # 排除 Qt DLL
            '--upx-exclude', 'PySide6*.dll',  # 排除 PySide6 DLL
        ])
    
    # 添加排除模块
    for exclude in excludes:
        opts.extend(['--exclude-module', exclude])
    
    # 添加数据文件
    for src, dst in datas:
        opts.extend(['--add-data', f'{src}{os.pathsep}{dst}'])
    
    # 运行打包
    run(opts)

if __name__ == '__main__':
    build() 