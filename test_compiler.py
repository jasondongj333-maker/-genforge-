"""
测试编译器能否检测到 AutoCAD DLL
"""
import os
import sys
sys.path.insert(0, "D:\\ai_cad_agent_001\\publish")

# 设置环境变量
os.environ["ACAD_PATH"] = r"C:\Program Files\Autodesk\AutoCAD 2024"
print(f"ACAD_PATH 设置为: {os.environ['ACAD_PATH']}")

# 测试编译器
from MCP.compiler import find_autocad_dlls

acad_dlls = find_autocad_dlls()
if acad_dlls:
    print("\n✅ 检测到 AutoCAD:")
    print(f"   版本: {acad_dlls['version']}")
    print(f"   acmgd: {acad_dlls['acmgd']}")
    print(f"   acdbmgd: {acad_dlls['acdbmgd']}")
else:
    print("\n❌ 未检测到 AutoCAD DLL")
    print("   请检查路径是否正确")
