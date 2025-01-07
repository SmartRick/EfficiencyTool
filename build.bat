@echo off
chcp 65001 > nul
title 打包程序

:: 检查是否安装 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

:: 运行打包脚本
echo 开始打包...
python build.py

if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)

echo 打包完成！
echo 程序位于 dist 目录下
pause 