"""
测试完整的编译流程（命令行模式）
"""
import os
import sys
sys.path.insert(0, "D:\\ai_cad_agent_001\\publish")

# 设置环境变量
os.environ["ACAD_PATH"] = r"C:\Program Files\Autodesk\AutoCAD 2024"
print(f"[1] ACAD_PATH 设置为: {os.environ['ACAD_PATH']}")

# 测试编译器
from MCP.compiler import CodeCompiler

print("\n[2] 初始化编译器...")
compiler = CodeCompiler()

# 测试代码 - 简单的直线绘制
test_code = """// 测试代码：绘制直线
Line line = new Line(
    new Point3d(0, 0, 0),
    new Point3d(1000, 1000, 0)
);
line.Layer = "A-AXIS";
btr.AppendEntity(line);
tr.AddNewlyCreatedDBObject(line, true);
successCount++;
"""

print("\n[3] 包裹沙箱模板...")
wrapped_code = compiler.wrap_in_sandbox(test_code)
print(f"   代码长度: {len(wrapped_code)} 字符")

print("\n[4] 开始编译...")
result = compiler.compile(wrapped_code, "autocad")

print("\n[5] 编译结果:")
if result["status"] == "success":
    print(f"✅ 编译成功!")
    print(f"   DLL 路径: {result['dll_path']}")
    print(f"   .cs 文件: {result['cs_file']}")
else:
    print(f"❌ 编译失败!")
    print(f"   错误信息: {result['message']}")

print("\n[6] 检查生成的临时文件...")
import glob
cs_files = glob.glob(str(compiler.temp_dir / "*.cs"))
csproj_files = glob.glob(str(compiler.temp_dir / "*.csproj"))

if cs_files:
    print(f"   .cs 文件: {cs_files}")
    print(f"   内容预览:")
    with open(cs_files[0], 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:30]):
            print(f"   {i+1:2d}: {line.rstrip()}")
    if len(lines) > 30:
        print(f"   ... (共 {len(lines)} 行)")

if csproj_files:
    print(f"\n   .csproj 文件: {csproj_files}")
    print(f"   内容:")
    with open(csproj_files[0], 'r', encoding='utf-8') as f:
        print(f.read())
