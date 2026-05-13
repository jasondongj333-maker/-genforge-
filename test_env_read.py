"""
测试编译器从 .env 文件读取 ACAD_PATH
"""
import os
import sys
sys.path.insert(0, "D:\\ai_cad_agent_001\\publish")

# 首先清除环境变量（模拟 EXE 运行时的环境）
if "ACAD_PATH" in os.environ:
    del os.environ["ACAD_PATH"]
    print("[1] 已清除系统环境变量 ACAD_PATH")

# 测试编译器
from MCP.compiler import find_autocad_dlls

print("\n[2] 测试 find_autocad_dlls()...")
acad_dlls = find_autocad_dlls()

if acad_dlls:
    print("\n✅ 检测成功!")
    print(f"   版本: {acad_dlls['version']}")
    print(f"   目录: {acad_dlls['dir']}")
    print(f"   acmgd.dll: {acad_dlls['acmgd']}")
    print(f"   acdbmgd.dll: {acad_dlls['acdbmgd']}")
else:
    print("\n❌ 未检测到 AutoCAD!")
    print("   请检查 .env 文件中的 ACAD_PATH 配置")
