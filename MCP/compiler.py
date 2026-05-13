"""
金锤子 (GenForge) - C# 代码编译器
参照 JZXZBOT：动态检测 AutoCAD 版本 → 生成正确引用路径 → dotnet build
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenForge.Compiler")

# AutoCAD DLL 标准位置（倒序优先高版本）
_ACAD_VERSIONS = list(range(2026, 2018, -1))
_ACAD_BASE = r"C:\Program Files\Autodesk"
_ACAD_BASE_X86 = r"C:\Program Files (x86)\Autodesk"

# 沙箱规范模板头（参照 JZXZBOT ArchitecturalCADDeveloper SKILL.md）
_SANDBOX_TEMPLATE_HEADER = """using System;
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

"""

_SANDBOX_TEMPLATE_FOOTER = """
                return $"[成功] 操作完成，处理 {successCount} 个对象。";
            }
            catch (System.Exception ex)
            {
                return $"[错误] 执行失败：{ex.Message}";
            }
        }

        // ─── AutoCAD 命令入口：加载 DLL 后在命令行输入 GFRUN 触发 ───
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


def find_autocad_dlls() -> dict | None:
    """
    自动检测已安装的 AutoCAD 版本，返回 DLL 路径字典
    
    搜索路径（按优先级）：
    1. 环境变量 ACAD_PATH
    2. .env 文件中的 ACAD_PATH（支持从 EXE 目录查找）
    3. 硬编码默认路径（作为最终备用）
    4. 标准安装路径遍历
    
    返回: {"acdbmgd": "...", "acmgd": "...", "version": "AutoCAD 2024"} 或 None
    """
    # 1. 尝试从环境变量读取
    acad_path_env = os.getenv("ACAD_PATH")
    if acad_path_env:
        acad_dir = Path(acad_path_env)
        if acad_dir.exists():
            acdbmgd = acad_dir / "acdbmgd.dll"
            acmgd   = acad_dir / "acmgd.dll"
            if acdbmgd.exists() and acmgd.exists():
                version = acad_dir.name.replace("AutoCAD ", "")
                logger.info(f"🎯 从环境变量检测到 AutoCAD {version}: {acad_dir}")
                return {
                    "acdbmgd": str(acdbmgd),
                    "acmgd":   str(acmgd),
                    "version": f"AutoCAD {version}",
                    "dir":     str(acad_dir),
                }
        else:
            logger.warning(f"⚠️ 环境变量 ACAD_PATH 指向的目录不存在: {acad_dir}")

    # 2. 尝试从 .env 文件读取（支持 EXE 运行时路径）
    try:
        env_path = None
        # 搜索顺序：EXE目录 -> 当前目录 -> 源代码目录
        possible_dirs = []
        
        # 2.1 EXE 所在目录（PyInstaller 打包后）
        if hasattr(sys, '_MEIPASS'):
            possible_dirs.append(Path(sys.executable).parent)
            possible_dirs.append(Path(sys._MEIPASS))
        
        # 2.2 当前工作目录
        possible_dirs.append(Path.cwd())
        
        # 2.3 源代码目录（开发模式）
        possible_dirs.append(Path(__file__).parent.parent)
        possible_dirs.append(Path(__file__).parent.parent.parent)
        
        # 查找 .env 文件
        for possible_dir in possible_dirs:
            test_path = possible_dir / ".env"
            if test_path.exists():
                env_path = test_path
                logger.info(f"📄 找到 .env 文件: {env_path}")
                break
        
        if env_path:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'ACAD_PATH' and value:
                            acad_dir = Path(value)
                            if acad_dir.exists():
                                acdbmgd = acad_dir / "acdbmgd.dll"
                                acmgd   = acad_dir / "acmgd.dll"
                                if acdbmgd.exists() and acmgd.exists():
                                    version = acad_dir.name.replace("AutoCAD ", "")
                                    logger.info(f"🎯 从 .env 文件检测到 AutoCAD {version}: {acad_dir}")
                                    return {
                                        "acdbmgd": str(acdbmgd),
                                        "acmgd":   str(acmgd),
                                        "version": f"AutoCAD {version}",
                                        "dir":     str(acad_dir),
                                    }
                            else:
                                logger.warning(f"⚠️ .env 中的 ACAD_PATH 指向的目录不存在: {acad_dir}")
    except Exception as e:
        logger.warning(f"⚠️ 读取 .env 文件失败: {e}")

    # 3. 硬编码默认路径（作为最终备用）
    logger.info("🔍 尝试硬编码默认路径...")
    default_paths = [
        r"C:\Program Files\Autodesk\AutoCAD 2024",
        r"C:\Program Files\Autodesk\AutoCAD 2023",
        r"C:\Program Files\Autodesk\AutoCAD 2022",
        r"C:\Program Files\Autodesk\AutoCAD 2021",
        r"C:\Program Files\Autodesk\AutoCAD 2020",
        r"C:\Program Files\Autodesk\AutoCAD 2019",
        r"C:\Program Files\Autodesk\AutoCAD 2018",
    ]
    for acad_path in default_paths:
        acad_dir = Path(acad_path)
        if acad_dir.exists():
            acdbmgd = acad_dir / "acdbmgd.dll"
            acmgd   = acad_dir / "acmgd.dll"
            if acdbmgd.exists() and acmgd.exists():
                version = acad_dir.name.replace("AutoCAD ", "")
                logger.info(f"🎯 从默认路径检测到 AutoCAD {version}: {acad_dir}")
                return {
                    "acdbmgd": str(acdbmgd),
                    "acmgd":   str(acmgd),
                    "version": f"AutoCAD {version}",
                    "dir":     str(acad_dir),
                }

    # 4. 搜索标准安装路径
    logger.info("🔍 搜索标准安装路径...")
    for version in _ACAD_VERSIONS:
        for base in [_ACAD_BASE, _ACAD_BASE_X86]:
            acad_dir = Path(base) / f"AutoCAD {version}"
            if not acad_dir.exists():
                continue

            acdbmgd = acad_dir / "acdbmgd.dll"
            acmgd   = acad_dir / "acmgd.dll"

            if acdbmgd.exists() and acmgd.exists():
                logger.info(f"🎯 检测到 AutoCAD {version}: {acad_dir}")
                return {
                    "acdbmgd": str(acdbmgd),
                    "acmgd":   str(acmgd),
                    "version": f"AutoCAD {version}",
                    "dir":     str(acad_dir),
                }

    logger.error("❌ 未检测到 AutoCAD DLL！请确保已安装 AutoCAD 2018-2026")
    logger.error("   或设置环境变量: set ACAD_PATH=C:\\Program Files\\Autodesk\\AutoCAD 2024")
    return None


class CodeCompiler:
    """C# 代码编译器 - 金锤子自主编译"""

    def __init__(self):
        # 路径：publish/../release/
        self.project_root = Path(__file__).parent.parent
        self.output_dir   = self.project_root.parent / "release"
        self.output_dir.mkdir(exist_ok=True)

        self.temp_dir = self.project_root / "Temp"
        self.temp_dir.mkdir(exist_ok=True)

        self.version   = 1
        self.acad_dlls = find_autocad_dlls()

    def compile(self, code: str, target: str = "autocad") -> dict:
        """
        编译 C# 代码为 DLL
        
        1. 对代码进行沙箱合规检查
        2. 保存 .cs 文件
        3. 生成 .csproj（含正确 AutoCAD 引用）
        4. dotnet build
        """
        logger.info(f"🔧 开始编译 (目标: {target})")

        try:
            # 检查 AutoCAD DLL（仅对 autocad 目标）
            # 每次编译前重新检测，确保环境变量变化后能生效
            if target == "autocad":
                self.acad_dlls = find_autocad_dlls()
                if not self.acad_dlls:
                    return {
                        "status": "error",
                        "message": "❌ 未检测到 AutoCAD DLL！\n\n"
                                   "请确保已安装 AutoCAD 2018-2026，或设置环境变量：\n"
                                   "PowerShell: $env:ACAD_PATH='C:\\Program Files\\Autodesk\\AutoCAD 2024'\n"
                                   "CMD: set ACAD_PATH=C:\\Program Files\\Autodesk\\AutoCAD 2024",
                    }

            # 沙箱合规检查
            violations = self._check_sandbox(code)
            if violations:
                return {
                    "status": "error",
                    "message": "代码违反沙箱规范:\n" + "\n".join(violations),
                }

            self._cleanup()

            cs_file    = self._save_code(code, target)
            csproj_file = self._create_project_file(target)

            result = self._run_dotnet_build(csproj_file, target)

            if result["success"]:
                logger.info(f"✅ 编译成功: {result['dll_path']}")
                return {
                    "status": "success",
                    "dll_path": result["dll_path"],
                    "cs_file":  str(cs_file),
                }
            else:
                logger.error(f"❌ 编译失败: {result['error']}")
                return {"status": "error", "message": result["error"]}

        except Exception as e:
            logger.error(f"❌ 编译异常: {e}")
            return {"status": "error", "message": str(e)}

    def wrap_in_sandbox(self, body_code: str) -> str:
        """
        将纯业务逻辑代码包裹进沙箱模板
        用于 LLM 只生成业务逻辑时自动补全
        """
        return _SANDBOX_TEMPLATE_HEADER + body_code + _SANDBOX_TEMPLATE_FOOTER

    # ─────────────────────────────────────────────────────────────
    # 私有方法
    # ─────────────────────────────────────────────────────────────

    def _check_sandbox(self, code: str) -> list:
        """沙箱合规检查（参照 JZXZBOT 禁令）"""
        violations = []
        checks = {
            "StartTransaction": "禁止调用 tr.StartTransaction()",
            "tr.Commit()":      "禁止调用 tr.Commit()",
            "LockDocument":     "禁止调用 doc.LockDocument()",
            "[CommandMethod":   "禁止使用 [CommandMethod] 特性（已由框架自动注入）",
        }
        for pattern, msg in checks.items():
            if pattern in code:
                violations.append(f"⚠️  {msg}")
        return violations

    def _cleanup(self):
        """清理临时文件"""
        for f in self.temp_dir.glob("*.cs"):
            try:
                f.unlink()
            except Exception:
                pass
        for f in self.temp_dir.glob("*.csproj"):
            try:
                f.unlink()
            except Exception:
                pass

    def _save_code(self, code: str, target: str) -> Path:
        """保存 .cs 文件，自动补全必要的 using 语句"""
        filename = f"genforge_{target}_v{self.version}.cs"
        cs_file  = self.temp_dir / filename
        
        # 自动补全 using 语句（防止 LLM 遗漏）
        if target == "autocad":
            code = self._ensure_autocad_usings(code)
        
        cs_file.write_text(code, encoding="utf-8")
        logger.info(f"📄 代码已保存: {cs_file}")
        return cs_file

    def _ensure_autocad_usings(self, code: str) -> str:
        """确保代码包含必要的 AutoCAD using 语句"""
        required_usings = [
            "using Autodesk.AutoCAD.ApplicationServices;",
            "using Autodesk.AutoCAD.DatabaseServices;",
            "using Autodesk.AutoCAD.Geometry;",
            "using Autodesk.AutoCAD.EditorInput;",
            "using Autodesk.AutoCAD.Colors;",
            "using Autodesk.AutoCAD.Runtime;",
        ]
        
        # 检查是否已有 using Autodesk.AutoCAD
        has_autocad = "using Autodesk.AutoCAD" in code
        
        if not has_autocad:
            # 在第一个 using 或 namespace 之前插入 AutoCAD using
            lines = code.split('\n')
            new_lines = []
            inserted = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                # 遇到 namespace 或 class 定义，在之前插入
                if not inserted and (stripped.startswith('namespace ') or stripped.startswith('public class')):
                    for u in required_usings:
                        new_lines.append(u)
                    new_lines.append('')  # 空行分隔
                    inserted = True
                new_lines.append(line)
            
            # 如果没找到插入点，在文件开头添加（跳过已有的 using）
            if not inserted:
                header_lines = [u for u in required_usings if u not in code]
                if header_lines:
                    # 找到第一个非空行的位置
                    start_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip():
                            start_idx = i
                            break
                    # 在开头插入
                    lines = header_lines + [''] + lines
            
            code = '\n'.join(new_lines)
            logger.info("✅ 自动补全了 AutoCAD using 语句")
        
        return code

    def _create_project_file(self, target: str) -> Path:
        """创建 .csproj 项目文件，含 AssemblyName 和 AutoCAD 引用"""
        dll_name   = f"GenForge_{target}_v{self.version}"
        csproj_name = f"{dll_name}.csproj"
        csproj_file = self.temp_dir / csproj_name

        # 引用节
        ref_block = ""
        if target == "autocad" and self.acad_dlls:
            ref_block = f"""
  <ItemGroup>
    <Reference Include="acmgd">
      <HintPath>{self.acad_dlls['acmgd']}</HintPath>
      <Private>False</Private>
    </Reference>
    <Reference Include="acdbmgd">
      <HintPath>{self.acad_dlls['acdbmgd']}</HintPath>
      <Private>False</Private>
    </Reference>
  </ItemGroup>"""
            logger.debug(f"✅ AutoCAD 引用已添加:")
            logger.debug(f"   acmgd: {self.acad_dlls['acmgd']}")
            logger.debug(f"   acdbmgd: {self.acad_dlls['acdbmgd']}")
        else:
            logger.warning(f"⚠️ 未添加 AutoCAD 引用! (target={target}, acad_dlls={self.acad_dlls})")

        csproj_content = f"""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net48</TargetFramework>
    <OutputType>Library</OutputType>
    <AssemblyName>{dll_name}</AssemblyName>
    <Nullable>disable</Nullable>
    <Optimize>true</Optimize>
  </PropertyGroup>{ref_block}
</Project>"""

        csproj_file.write_text(csproj_content, encoding="utf-8")
        logger.info(f"📄 项目文件已创建: {csproj_file}")
        
        # 调试：打印项目文件内容
        logger.debug(f"项目文件内容:\n{csproj_content}")
        return csproj_file

    def _run_dotnet_build(self, csproj_file: Path, target: str) -> dict:
        """执行 dotnet build"""
        try:
            output_dir = self.output_dir / target
            output_dir.mkdir(exist_ok=True)

            result = subprocess.run(
                ["dotnet", "build", str(csproj_file),
                 "-o", str(output_dir),
                 "-c", "Release",
                 "--nologo"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(self.temp_dir),
                timeout=60,
            )

            dll_name = f"GenForge_{target}_v{self.version}.dll"
            dll_path = output_dir / dll_name

            if result.returncode == 0 and dll_path.exists():
                self.version += 1
                return {
                    "success":  True,
                    "dll_path": str(dll_path),
                    "output":   result.stdout,
                }
            else:
                error_msg = result.stdout + "\n" + result.stderr
                # 如果 DLL 存在但 returncode 非 0（警告情况），仍视为成功
                if dll_path.exists():
                    logger.warning("编译有警告但 DLL 已生成，视为成功")
                    self.version += 1
                    return {
                        "success":  True,
                        "dll_path": str(dll_path),
                        "output":   result.stdout,
                    }
                return {"success": False, "error": error_msg.strip()}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "编译超时（>60s）"}
        except FileNotFoundError:
            return {"success": False, "error": "未找到 dotnet 命令，请安装 .NET SDK"}
        except Exception as e:
            return {"success": False, "error": str(e)}
