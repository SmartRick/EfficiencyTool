@echo off
chcp 65001 > nul

:: 获取当前目录的完整路径
set "SCRIPT_PATH=%~dp0run.bat"

:: 创建快捷方式
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\休息提醒工具.lnk'); $SC.TargetPath = '%SCRIPT_PATH%'; $SC.WorkingDirectory = '%~dp0'; $SC.IconLocation = '%~dp0src\assets\icons\app.ico'; $SC.Save()"

echo 快捷方式已创建到桌面！
pause 