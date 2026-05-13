"""
金锤子 (GenForge) - 完整诊断测试
测试带 CAD 引用的编译
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger("GenForge.Compiler")

ACAD_PATH = r"C:\Program Files\Autodesk\AutoCAD 2024"

_TEST_CAD_CODE = """
using System;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;

namespace GenForgeCADTest
{
    public class TestClass
    {
        public string TestMethod()
        {
            return "CAD Reference OK!";
        }
    }
}
"""

def test_cad_compilation() -> dict:
    print("=" * 50)
    print("TEST: CAD compilation (with AutoCAD references)")
    print("=" * 50)
    print(f"ACAD_PATH: {ACAD_PATH}")

    temp_dir = Path(os.getenv("TEMP", "C:\\Users\\Jason\\AppData\\Local\\Temp")) / "genforge_cad_test"
    temp_dir.mkdir(exist_ok=True)

    cs_file = temp_dir / "test_cad.cs"
    cs_file.write_text(_TEST_CAD_CODE, encoding="utf-8")

    csproj_file = temp_dir / "test_cad.csproj"
    csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <OutputType>Library</OutputType>
    <AssemblyName>GenForgeCADTest</AssemblyName>
    <Nullable>disable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="acmgd">
      <HintPath>{ACAD_PATH}\\acmgd.dll</HintPath>
      <Private>False</Private>
    </Reference>
    <Reference Include="acdbmgd">
      <HintPath>{ACAD_PATH}\\acdbmgd.dll</HintPath>
      <Private>False</Private>
    </Reference>
  </ItemGroup>
</Project>"""
    csproj_file.write_text(csproj_content, encoding="utf-8")

    print(f"CS file: {cs_file}")
    print(f"Project file: {csproj_file}")
    print(f"Project content:\n{csproj_content}")

    try:
        result = subprocess.run(
            ["dotnet", "build", str(csproj_file),
             "-o", str(temp_dir / "output"),
             "-c", "Release",
             "--nologo"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(temp_dir),
            timeout=60,
        )

        dll_path = temp_dir / "output" / "GenForgeCADTest.dll"

        if result.returncode == 0 and dll_path.exists():
            print(f"[OK] DLL created: {dll_path}")
            return {"success": True, "dll_path": str(dll_path)}
        else:
            print(f"[FAIL] Build failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return {"success": False, "error": result.stdout + "\n" + result.stderr}

    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GenForge CAD Compilation Diagnostic Test")
    print("=" * 60 + "\n")

    result = test_cad_compilation()

    print("\n" + "=" * 60)
    if result["success"]:
        print("RESULT: CAD compilation is OK")
        print(f"DLL: {result['dll_path']}")
    else:
        print("RESULT: CAD compilation FAILED")
        print(f"ERROR: {result['error']}")
    print("=" * 60 + "\n")
