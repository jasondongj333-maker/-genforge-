@echo off
chcp 65001 >nul
echo ============================================
echo   金锤子 GenForge - PyInstaller 打包脚本
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] 清理旧构建...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [2/3] 开始打包（PyInstaller 6.20.0）...
echo.

"D:\anaconda\python.exe" -m PyInstaller ^
    --name "GenForge" ^
    --onefile ^
    --windowed ^
    --add-data "Settings;Settings" ^
    --add-data "Core;Core" ^
    --add-data "MCP;MCP" ^
    --add-data "Skills;Skills" ^
    --add-data "UI;UI" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.scrolledtext ^
    --hidden-import=tiktoken ^
    --hidden-import=tiktoken.ext ^
    --hidden-import=tiktoken.implementations ^
    --collect-all=tiktoken ^
    --noconfirm ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败，错误码: %errorlevel%
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] 验证输出...
if exist "dist\GenForge.exe" (
    for %%A in ("dist\GenForge.exe") do echo    文件: %%~nxA
    for %%A in ("dist\GenForge.exe") do echo    大小: %%~zA 字节
    echo.
    echo    ============================================
    echo      打包成功！
    echo      输出路径: dist\GenForge.exe
    echo    ============================================
) else (
    echo    [错误] 未找到 GenForge.exe
    exit /b 1
)

echo.
echo [完成] 双击运行 dist\GenForge.exe 启动金锤子
pause
