"""
仅测试编译功能（绕过沙箱检查）
"""
import os
import sys
import subprocess
from pathlib import Path

# 设置环境变量
os.environ["ACAD_PATH"] = r"C:\Program Files\Autodesk\AutoCAD 2024"

# 临时目录
temp_dir = Path(r"D:\ai_cad_agent_001\publish\Temp")
temp_dir.mkdir(exist_ok=True)
output_dir = Path(r"D:\ai_cad_agent_001\release\autocad")
output_dir.mkdir(exist_ok=True)

# 完整的测试代码（包括 using 和命名空间）
test_cs_content = """using System;
using System.Collections.Generic;
using System.Linq;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Colors;
using Autodesk.AutoCAD.Runtime;

namespace AiGeneratedCode
{
    public class DynamicTask
    {
        public string Execute(Document doc, Transaction tr, BlockTableRecord btr)
        {
            int successCount = 0;
            try
            {
                Editor ed = doc.Editor;
                Database db = doc.Database;

                // 绘制直线
                Line line = new Line(
                    new Point3d(0, 0, 0),
                    new Point3d(1000, 1000, 0)
                );
                line.Layer = "A-AXIS";
                btr.AppendEntity(line);
                tr.AddNewlyCreatedDBObject(line, true);
                successCount++;

                return $"[成功] 操作完成，处理 {successCount} 个对象。";
            }
            catch (System.Exception ex)
            {
                return $"[错误] 执行失败：{ex.Message}";
            }
        }

        [Autodesk.AutoCAD.Runtime.CommandMethod("GFRUN", Autodesk.AutoCAD.Runtime.CommandFlags.Session)]
        public void GFRun()
        {
            var doc = Autodesk.AutoCAD.ApplicationServices.Application.DocumentManager.MdiActiveDocument;
            if (doc == null) return;
            doc.LockDocument();
            using (var tr = doc.Database.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)doc.Database.BlockTableId.GetObject(OpenMode.ForRead);
                var btr = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                var result = Execute(doc, tr, btr);
                tr.Commit();
                doc.Editor.WriteMessage("\\n" + result);
            }
        }
    }
}
"""

# 保存 .cs 文件
cs_file = temp_dir / "test_compile.cs"
cs_file.write_text(test_cs_content, encoding="utf-8")
print(f"✅ .cs 文件已创建: {cs_file}")

# 创建 .csproj 文件
csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <OutputType>Library</OutputType>
    <AssemblyName>TestCompile</AssemblyName>
    <Nullable>disable</Nullable>
    <Optimize>true</Optimize>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="acmgd">
      <HintPath>C:\Program Files\Autodesk\AutoCAD 2024\acmgd.dll</HintPath>
      <Private>False</Private>
    </Reference>
    <Reference Include="acdbmgd">
      <HintPath>C:\Program Files\Autodesk\AutoCAD 2024\acdbmgd.dll</HintPath>
      <Private>False</Private>
    </Reference>
  </ItemGroup>
</Project>"""

csproj_file = temp_dir / "TestCompile.csproj"
csproj_file.write_text(csproj_content, encoding="utf-8")
print(f"✅ .csproj 文件已创建: {csproj_file}")
print(f"\n.csproj 内容:\n{csproj_content}")

# 执行编译
print("\n\n🚀 开始编译...")
result = subprocess.run(
    ["dotnet", "build", str(csproj_file),
     "-o", str(output_dir),
     "-c", "Release",
     "--nologo"],
    capture_output=True,
    text=True,
    encoding="gbk",
    errors="replace",
    cwd=str(temp_dir),
    timeout=60,
)

print("\n=== 编译输出 ===")
print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\n返回码: {result.returncode}")

# 检查结果
dll_path = output_dir / "TestCompile.dll"
if result.returncode == 0 and dll_path.exists():
    print("\n✅ 编译成功！")
    print(f"   DLL 文件: {dll_path}")
    file_size = dll_path.stat().st_size / 1024
    print(f"   文件大小: {file_size:.2f} KB")
else:
    print("\n❌ 编译失败！")
