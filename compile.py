"""
CAD C# 代码编译器
用法: python compile.py "path/to/code.cs"
"""

import os
import sys
import subprocess

def find_autocad_dlls():
    """查找 AutoCAD DLL"""
    acad_paths = []

    for version in range(2026, 2018, -1):
        path = os.path.join("C:", "Program Files", "Autodesk", f"AutoCAD {version}")
        if os.path.exists(path):
            acad_paths.append(path)

        path_x86 = os.path.join("C:", "Program Files (x86)", "Autodesk", f"AutoCAD {version}")
        if os.path.exists(path_x86):
            acad_paths.append(path_x86)

    dlls = {}
    for base_path in acad_paths:
        inc_path = os.path.join(base_path, "inc")
        if os.path.exists(inc_path):
            dlls['acdbmgd'] = os.path.join(inc_path, "acdbmgd.dll")
            dlls['acmgd'] = os.path.join(inc_path, "acmgd.dll")
            dlls['accore'] = os.path.join(inc_path, "accore.dll")
            return dlls

    return None

def compile_csharp(source_file, output_dir="Compiled"):
    """编译 C# 文件"""
    print("=" * 50)
    print("   CAD C# 代码编译器")
    print("=" * 50)
    print()

    if not os.path.exists(source_file):
        print(f"[错误] 源文件不存在: {source_file}")
        return False

    os.makedirs(output_dir, exist_ok=True)
    output_dll = os.path.join(output_dir, "output.dll")

    acad_dlls = find_autocad_dlls()

    if acad_dlls:
        print("[找到] AutoCAD DLL")
        for name, path in acad_dlls.items():
            if os.path.exists(path):
                print(f"  - {name}: {path}")
    else:
        print("[警告] 未找到 AutoCAD DLL，编译可能失败")

    print()
    print(f"[编译中] {source_file}")
    print()

    refs = []
    if acad_dlls:
        for name in ['acdbmgd', 'acmgd', 'accore']:
            path = acad_dlls.get(name)
            if path and os.path.exists(path):
                refs.extend(['-r', path])

    try:
        result = subprocess.run(
            ['dotnet', 'build', '-o', output_dir, source_file],
            capture_output=True,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print()
            print(f"[成功] 编译完成!")
            print(f"输出文件: {output_dll}")
            print()
            print("[下一步]")
            print("1. 打开 AutoCAD")
            print("2. 输入命令: NETLOAD")
            print(f"3. 选择: {output_dll}")
            print("4. 输入命令: DrawVillaSavoye")
            return True
        else:
            print()
            print("[失败] 编译失败")
            return False

    except Exception as e:
        print(f"[错误] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python compile.py <source_file.cs>")
        print("示例: python compile.py Source/VillaSavoye.cs")
        sys.exit(1)

    source = sys.argv[1]
    compile_csharp(source)
