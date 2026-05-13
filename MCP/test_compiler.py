"""
金锤子 (GenForge) - C# 编译器诊断测试
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger("GenForge.Compiler")

_TEST_SIMPLE_CODE = """
using System;

namespace GenForgeTest
{
    public class TestClass
    {
        public string SayHello()
        {
            return "Hello from GenForge!";
        }
    }
}
"""

def test_simple_compilation() -> dict:
    print("=" * 50)
    print("TEST: Simple compilation (no CAD references)")
    print("=" * 50)

    temp_dir = Path(os.getenv("TEMP", "C:\\Users\\Jason\\AppData\\Local\\Temp")) / "genforge_test"
    temp_dir.mkdir(exist_ok=True)

    cs_file = temp_dir / "test.cs"
    cs_file.write_text(_TEST_SIMPLE_CODE, encoding="utf-8")

    csproj_file = temp_dir / "test.csproj"
    csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <OutputType>Library</OutputType>
    <AssemblyName>GenForgeTest</AssemblyName>
  </PropertyGroup>
</Project>"""
    csproj_file.write_text(csproj_content, encoding="utf-8")

    print(f"CS file: {cs_file}")
    print(f"Project file: {csproj_file}")

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

        dll_path = temp_dir / "output" / "GenForgeTest.dll"

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
    print("GenForge Compiler Diagnostic Test")
    print("=" * 60 + "\n")

    result = test_simple_compilation()

    print("\n" + "=" * 60)
    if result["success"]:
        print("RESULT: dotnet environment is OK")
        print(f"DLL: {result['dll_path']}")
    else:
        print("RESULT: dotnet environment has issues")
        print(f"ERROR: {result['error']}")
    print("=" * 60 + "\n")
