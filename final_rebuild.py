"""
最终重新打包脚本
"""
import subprocess
import sys
import os
import time

# 删除旧的 build 和 dist 目录
print("[1] 删除旧的构建文件...")
try:
    import shutil
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    print("   ✅ 已删除")
except Exception as e:
    print(f"   ⚠️ 删除失败: {e}")
    time.sleep(1)

# 执行打包
print("\n[2] 执行 PyInstaller 打包...")
cmd = [
    "python", "-m", "PyInstaller",
    "--name", "GenForge",
    "--onefile",
    "--windowed",
    "--add-data", "Settings;Settings",
    "--add-data", "Core;Core",
    "--add-data", "MCP;MCP",
    "--add-data", "Skills;Skills",
    "--add-data", "UI;UI",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.ttk",
    "--hidden-import", "tkinter.messagebox",
    "--hidden-import", "tkinter.filedialog",
    "--hidden-import", "tkinter.scrolledtext",
    "--hidden-import", "tiktoken",
    "--collect-all", "tiktoken",
    "--noconfirm",
    "main.py"
]

print(f"   执行命令: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=False)

# 检查结果
print(f"\n[3] 打包返回码: {result.returncode}")

exe_path = "dist/GenForge.exe"
if os.path.exists(exe_path):
    file_size = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"   ✅ 打包成功！")
    print(f"   文件: {exe_path}")
    print(f"   大小: {file_size:.2f} MB")

    # 复制 .env 文件到 dist 目录
    print("\n[4] 复制 .env 文件到 dist 目录...")
    import shutil
    if os.path.exists(".env"):
        shutil.copy(".env", "dist/.env")
        print("   ✅ 已复制")

else:
    print(f"   ❌ 打包失败！")
