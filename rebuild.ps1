# 重新打包脚本
Write-Host "=== 金锤子 GenForge 重新打包 ===" -ForegroundColor Cyan

# 停止正在运行的 GenForge 进程
Write-Host "`n[1/3] 停止正在运行的进程..." -ForegroundColor Yellow
Get-Process GenForge -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 清理旧构建
Write-Host "`n[2/3] 清理旧构建..." -ForegroundColor Yellow
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# 执行打包
Write-Host "`n[3/3] 执行 PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller `
    --name "GenForge" `
    --onefile `
    --windowed `
    --add-data "Settings;Settings" `
    --add-data "Core;Core" `
    --add-data "MCP;MCP" `
    --add-data "Skills;Skills" `
    --add-data "UI;UI" `
    --hidden-import=tkinter `
    --hidden-import=tkinter.ttk `
    --hidden-import=tkinter.messagebox `
    --hidden-import=tkinter.filedialog `
    --hidden-import=tkinter.scrolledtext `
    --hidden-import=tiktoken `
    --collect-all=tiktoken `
    --noconfirm `
    main.py

# 验证结果
Write-Host "`n=== 打包完成 ===" -ForegroundColor Cyan
$exePath = "dist\GenForge.exe"
if (Test-Path $exePath) {
    $fileInfo = Get-Item $exePath
    Write-Host "✅ 打包成功！" -ForegroundColor Green
    Write-Host "   文件: $exePath"
    Write-Host "   大小: $($fileInfo.Length / 1MB):F2 MB"
} else {
    Write-Host "❌ 打包失败！" -ForegroundColor Red
    exit 1
}
