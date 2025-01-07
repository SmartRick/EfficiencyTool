@echo off
chcp 65001 > nul
title 休息提醒工具

:: 检查是否存在虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 未检测到虚拟环境，将使用系统 Python
)

:: 检查依赖是否安装
echo 检查依赖...
python -c "import PySide6" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖安装失败！
        pause
        exit /b 1
    )
)

:: 运行程序
echo 启动程序...
python src/main.py
if errorlevel 1 (
    echo 程序异常退出！
    pause
) 