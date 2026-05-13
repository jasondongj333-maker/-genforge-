@echo off
chcp 65001 >nul
echo ============================================
echo   CAD C# 代码编译器
echo ============================================
echo.

:: 检查参数
if "%~1"=="" (
    echo [错误] 请提供要编译的 C# 文件路径
    echo 用法: compile.bat "path\to\your\code.cs"
    exit /b 1
)

set SOURCE_FILE=%~1
set OUTPUT_DIR=D:\TRAE_PROJECT\CAD_AGENT\Compiled

:: 创建输出目录
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: 查找 AutoCAD DLL
set ACAD_PATH=
for /d %%D in ("C:\Program Files\Autodesk\AutoCAD 20*") do (
    set ACAD_PATH=%%D
)

if "%ACAD_PATH%"=="" (
    echo [警告] 未找到 AutoCAD，将尝试使用默认引用编译
    set REF_OPTS=
) else (
    echo [信息] 找到 AutoCAD: %ACAD_PATH%
    set REF_OPTS=-r:"%ACAD_PATH%\inc\acdbmgd.dll" -r:"%ACAD_PATH%\inc\acmgd.dll" -r:"%ACAD_PATH%\inc\ Autodesk.AutoCAD.Runtime.dll"
)

:: 编译命令
echo.
echo [编译中] %SOURCE_FILE%
echo.

:: 使用 csc.exe 编译（如果可用）
where csc.exe >nul 2>&1
if %errorlevel%==0 (
    csc.exe /target:library /out:"%OUTPUT_DIR%\output.dll" %REF_OPTS% "%SOURCE_FILE%"
) else (
    :: 备选方案：使用 dotnet roslyn
    echo [信息] 使用 Roslyn 编译器
    dotnet script "%SOURCE_FILE%" --output "%OUTPUT_DIR%\output.dll" 2>nul
    if %errorlevel% neq 0 (
        echo [错误] 编译失败
        echo 请确保：
        echo 1. 系统已安装 .NET SDK
        echo 2. AutoCAD 已安装
        exit /b 1
    )
)

if %errorlevel%==0 (
    echo.
    echo [成功] 编译完成！
    echo 输出文件: %OUTPUT_DIR%\output.dll
    echo.
    echo [下一步]
    echo 1. 打开 AutoCAD
    echo 2. 输入命令: NETLOAD
    echo 3. 选择编译好的 DLL
    echo 4. 输入命令: DrawVillaSavoye
) else (
    echo.
    echo [失败] 编译失败
    exit /b 1
)
