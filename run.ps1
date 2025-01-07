# 设置标题
$host.UI.RawUI.WindowTitle = "休息提醒工具"

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 函数：检查并安装依赖
function Install-Dependencies {
    Write-Host "检查依赖..." -ForegroundColor Yellow
    try {
        python -c "import PySide6" 2>$null
    }
    catch {
        Write-Host "正在安装依赖..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "依赖安装失败！" -ForegroundColor Red
            Read-Host "按回车键退出"
            exit 1
        }
    }
}

# 检查虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "正在激活虚拟环境..." -ForegroundColor Green
    . .\venv\Scripts\Activate.ps1
}
else {
    Write-Host "未检测到虚拟环境，将使用系统 Python" -ForegroundColor Yellow
}

# 安装依赖
Install-Dependencies

# 运行程序
Write-Host "启动程序..." -ForegroundColor Green
try {
    python src/main.py
}
catch {
    Write-Host "程序异常退出！" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "按回车键退出"
} 