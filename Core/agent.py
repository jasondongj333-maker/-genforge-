"""
金锤子 (GenForge) - 核心智能体
参照 JZXZBOT 架构：多角色 Architect + CADDeveloper 协作流程
"""
import sys
import json
import logging
from pathlib import Path

# 确保项目根目录在 sys.path 中
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from Core.intent_parser import IntentParser
from Core.llm_client import LLMClient
from Core.skill_loader import SkillLoader
from MCP.compiler import CodeCompiler
from MCP.cad_connector import CADConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenForge.Agent")


class GenForgeAgent:
    """
    金锤子核心智能体 - 多角色协作架构
    
    角色分工（参照 JZXZBOT）：
      Architect Agent    → 解析需求，制定绘图计划，输出结构化参数
      CADDeveloper Agent → 接收参数，生成符合沙箱规范的 C# 代码
    """

    def __init__(self):
        self.intent_parser = IntentParser()
        self.llm_client = LLMClient()
        self.skill_loader = SkillLoader()
        self.compiler = CodeCompiler()
        self.connector = CADConnector()

        # 加载技能
        self.skills = self.skill_loader.load_all()
        logger.info(f"✅ 已加载 {len(self.skills)} 个技能: {list(self.skills.keys())}")

        # 对话历史（多轮）
        self.conversation_history = []
        self.last_generated_code = None
        self.last_dll_path = None

    # ─────────────────────────────────────────────
    # 公开入口
    # ─────────────────────────────────────────────

    def process_request(self, user_input: str) -> dict:
        """
        处理用户请求，返回结构化结果
        返回: {
            "status": "success" | "error" | "code_only",
            "message": str,        # 给用户看的摘要
            "architect_plan": str, # Architect 输出（可选）
            "code": str,           # 生成的 C# 代码（可选）
            "dll_path": str,       # 编译产出（可选）
            "cad_result": str,     # CAD 执行结果（可选）
        }
        """
        logger.info(f"🔨 收到请求: {user_input}")

        # 1. 快速关键词预判：是否是 CAD 绘图类请求
        intent = self.intent_parser.parse(user_input)

        if intent and intent.get("type") == "cad_draw":
            return self._run_cad_pipeline(user_input, intent)
        else:
            # 普通对话：直接用 LLM 回答
            return self._run_chat(user_input)

    def process_code_only(self, user_input: str) -> dict:
        """
        仅生成代码，不编译执行（用于预览）
        """
        plan = self._architect_plan(user_input)
        code = self._developer_generate(user_input, plan)
        self.last_generated_code = code
        return {
            "status": "code_only",
            "message": "代码已生成，未执行",
            "architect_plan": plan,
            "code": code,
        }

    def execute_last_code(self) -> dict:
        """
        执行上次生成的代码（编译 + 发送到 CAD）
        """
        if not self.last_generated_code:
            return {"status": "error", "message": "没有待执行的代码，请先生成代码"}
        return self._compile_and_run(self.last_generated_code)

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self.llm_client.clear_history()
        logger.info("🗑️ 对话历史已清空")

    # ─────────────────────────────────────────────
    # 内部流程
    # ─────────────────────────────────────────────

    def _run_cad_pipeline(self, user_input: str, intent: dict) -> dict:
        """
        CAD 绘图完整流水线：Architect → COM 直接执行
        
        使用 COM 自动化方案，无需编译 DLL，直接发送命令到 AutoCAD
        """

        # Phase 1: Architect 制定计划
        logger.info("🏛️  [Architect] 正在分析需求，制定绘图计划...")
        try:
            plan = self._architect_plan(user_input)
            logger.info(f"🏛️  [Architect] 计划完成:\n{plan}")
        except RuntimeError as e:
            return {
                "status": "error",
                "message": f"🏛️  [Architect] 绘图计划：\n{str(e)}\n\n💻 [CAD执行] 执行跳过",
            }

        # Phase 2: 连接 CAD 并执行
        logger.info("🔗 [CAD] 正在连接 AutoCAD...")
        if not self.connector.connect():
            return {
                "status": "error",
                "message": "❌ 无法连接到 AutoCAD，请确保 AutoCAD 已打开",
                "architect_plan": plan,
            }

        # Phase 3: 根据计划执行命令
        logger.info("🚀 [CAD] 正在执行命令...")
        try:
            result = self._execute_plan(plan)
        except RuntimeError as e:
            return {
                "status": "error",
                "message": f"🏛️  [建筑师] 绘图计划：\n{plan}\n\n💻 [CAD执行] 执行失败：\n{str(e)}",
                "architect_plan": plan,
            }

        result["architect_plan"] = plan
        return result

    def _run_chat(self, user_input: str) -> dict:
        """普通对话回复"""
        architect_skill = self.skills.get("Architect", "")
        response = self.llm_client.chat(user_input, system_prompt=architect_skill)
        return {
            "status": "success",
            "message": response,
        }

    def _architect_plan(self, user_input: str) -> str:
        """
        Architect Agent：解析需求，输出结构化绘图计划
        参照 JZXZBOT Architect SKILL.md 角色定义
        """
        architect_skill = self.skills.get("Architect", "")
        prompt = f"""作为建筑设计师，请分析以下 CAD 绘图需求，并输出结构化绘图计划（JSON格式）：

用户需求：{user_input}

请输出包含以下字段的 JSON 计划：
{{
  "task_type": "draw_line | draw_rectangle | draw_wall | draw_axis | create_layer",
  "elements": [
    {{
      "type": "line | rectangle | wall | axis | layer",
      "params": {{
        "start_x": 0,
        "start_y": 0,
        "end_x": 1000,
        "end_y": 1000,
        "layer": "A-AXIS"
      }}
    }}
  ],
  "cad_commands": [
    "命令1",
    "命令2"
  ]
}}

直接输出 JSON，不要添加额外说明。"""

        try:
            plan_str = self.llm_client.chat(prompt, system_prompt=architect_skill, save_history=False)
        except RuntimeError as e:
            raise RuntimeError(f"[LLM错误] {e}") from e

        plan_str = plan_str.strip()
        if plan_str.startswith("```"):
            lines = plan_str.split("\n")
            plan_str = "\n".join(lines[1:-1])

        return plan_str

    def _execute_plan(self, plan: str) -> dict:
        """
        根据 Architect 的计划，直接通过 COM 执行 AutoCAD 命令
        """
        import json
        
        try:
            plan_obj = json.loads(plan)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"计划解析失败: {e}")
        
        task_type = plan_obj.get("task_type", "")
        elements = plan_obj.get("elements", [])
        commands = plan_obj.get("cad_commands", [])
        
        success_count = 0
        failed_commands = []
        
        # 执行预定义命令
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:
                if self.connector.send_command(cmd):
                    success_count += 1
                else:
                    failed_commands.append(cmd)
        
        # 根据元素类型执行
        for element in elements:
            elem_type = element.get("type", "")
            params = element.get("params", {})
            
            try:
                if elem_type == "layer":
                    layer_name = params.get("name", "0")
                    color = params.get("color", 7)
                    if self.connector.create_layer(layer_name, color):
                        success_count += 1
                    else:
                        failed_commands.append(f"创建图层 {layer_name}")
                
                elif elem_type in ("line", "axis"):
                    x1 = params.get("start_x", 0)
                    y1 = params.get("start_y", 0)
                    x2 = params.get("end_x", 0)
                    y2 = params.get("end_y", 0)
                    layer = params.get("layer", "0")
                    if self.connector.draw_line(x1, y1, x2, y2, layer):
                        success_count += 1
                    else:
                        failed_commands.append(f"绘制直线 ({x1},{y1})-({x2},{y2})")
                
                elif elem_type == "rectangle":
                    x1 = params.get("start_x", 0)
                    y1 = params.get("start_y", 0)
                    x2 = params.get("end_x", 0)
                    y2 = params.get("end_y", 0)
                    layer = params.get("layer", "0")
                    if self.connector.draw_rectangle(x1, y1, x2, y2, layer):
                        success_count += 1
                    else:
                        failed_commands.append(f"绘制矩形 ({x1},{y1})-({x2},{y2})")
                
                elif elem_type in ("wall", "polyline"):
                    points = params.get("points", [])
                    layer = params.get("layer", "A-WALL")
                    if points and self.connector.draw_polyline(points, layer):
                        success_count += 1
                    else:
                        failed_commands.append(f"绘制多段线")
                
                elif elem_type == "circle":
                    x = params.get("x", 0)
                    y = params.get("y", 0)
                    radius = params.get("radius", 500)
                    layer = params.get("layer", "0")
                    if self.connector.draw_circle(x, y, radius, layer):
                        success_count += 1
                    else:
                        failed_commands.append(f"绘制圆 ({x},{y}) r={radius}")
                        
            except Exception as e:
                failed_commands.append(f"{elem_type}: {e}")
        
        # 缩放到全图
        self.connector.zoom_extents()
        
        if failed_commands:
            msg = f"✅ 执行完成，但 {len(failed_commands)} 个命令失败:\n" + "\n".join(failed_commands)
            return {"status": "partial", "message": msg}
        
        return {
            "status": "success",
            "message": f"✅ 执行成功！共执行 {success_count} 个命令",
        }

    def _developer_generate(self, user_input: str, plan: str) -> str:
        """
        CAD Developer Agent：根据计划生成符合 IAiCadCommand 沙箱规范的 C# 代码
        参照 JZXZBOT ArchitecturalCADDeveloper SKILL.md
        """
        developer_skill = self.skills.get("CADDeveloper", "")
        
        code_prompt = f"""用户需求：{user_input}

建筑师制定的计划：
{plan}

请严格按照以下模板生成 C# AutoCAD 代码：

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Colors;
using Autodesk.AutoCAD.Runtime;

namespace AiGeneratedCode
{{
    public class DynamicTask
    {{
        public string Execute(Document doc, Transaction tr, BlockTableRecord btr)
        {{
            int successCount = 0;
            try
            {{
                Editor ed = doc.Editor;
                Database db = doc.Database;

                // --- 绘图逻辑 ---
                // 新实体必须: btr.AppendEntity(ent); tr.AddNewlyCreatedDBObject(ent, true);
                // 禁止: tr.StartTransaction(), tr.Commit(), doc.LockDocument()
                // 禁止: [CommandMethod] 特性

                return $"[成功] 完成，处理了 {{successCount}} 个对象。";
            }}
            catch (System.Exception ex)
            {{
                return $"[错误] 执行失败：{{ex.Message}}";
            }}
        }}
    }}
}}
```

要求：
1. 只输出代码块内的 C# 代码，不要加解释
2. 使用 AddVertexAt 而非 AddVertex
3. 使用 tr.AddNewlyCreatedDBObject(ent, true)
4. 遵循中国建筑 CAD 图层标准（A-WALL/A-DOOR/A-AXIS 等）
5. 参数使用毫米单位"""

        try:
            code_str = self.llm_client.chat(code_prompt, system_prompt=developer_skill, save_history=False)
        except RuntimeError as e:
            raise RuntimeError(f"[LLM错误] {e}") from e

        # 提取代码块
        code_str = code_str.strip()
        if "```csharp" in code_str:
            start = code_str.find("```csharp") + 9
            end = code_str.rfind("```")
            code_str = code_str[start:end].strip()
        elif "```" in code_str:
            start = code_str.find("```") + 3
            end = code_str.rfind("```")
            code_str = code_str[start:end].strip()

        # 基础验证：检查是否像 C# 代码（防止 LLM 返回错误提示文本）
        if not code_str or len(code_str) < 20 or code_str.startswith("[LLM错误]") or code_str.startswith("```"):
            raise RuntimeError(
                "LLM 返回内容异常，可能是 API 鉴权失败或限流。"
                "请检查 DeepSeek API Key 配置，或稍后重试。"
            )

        return code_str

    def _compile_and_run(self, code: str) -> dict:
        """编译并在 AutoCAD 中执行"""

        # 编译
        logger.info("🔧 [Compiler] 正在编译...")
        compile_result = self.compiler.compile(code, target="autocad")

        if compile_result["status"] != "success":
            return {
                "status": "error",
                "message": f"编译失败:\n{compile_result.get('message', '未知错误')}",
            }

        dll_path = compile_result["dll_path"]
        self.last_dll_path = dll_path
        logger.info(f"✅ [Compiler] 编译成功: {dll_path}")

        # 连接 CAD
        logger.info("🔗 [CAD] 正在连接 AutoCAD...")
        if not self.connector.connect():
            return {
                "status": "error",
                "message": "❌ 无法连接到 AutoCAD，请确保 AutoCAD 已打开\n\n"
                           f"编译产物（可手动加载）:\n{dll_path}",
                "dll_path": dll_path,
            }

        # 加载 DLL
        logger.info(f"📦 [CAD] 加载 DLL: {dll_path}")
        if not self.connector.load_dll(dll_path):
            return {
                "status": "error",
                "message": f"❌ DLL 加载失败\n路径: {dll_path}",
                "dll_path": dll_path,
            }

        # 执行命令（DynamicTask 不需要显式命令，DLL 加载后自动执行或由宿主触发）
        logger.info("🚀 [CAD] DLL 已加载，等待执行...")

        return {
            "status": "success",
            "message": f"✅ 执行成功！\nDLL: {dll_path}",
            "dll_path": dll_path,
        }

    # ─────────────────────────────────────────────
    # 辅助方法
    # ─────────────────────────────────────────────

    def get_skill_list(self) -> list:
        """返回已加载的技能列表"""
        return list(self.skills.keys())

    def get_status(self) -> dict:
        """返回当前状态"""
        return {
            "skills_loaded": list(self.skills.keys()),
            "history_turns": len(self.conversation_history),
            "last_dll": self.last_dll_path,
            "cad_connected": self.connector.is_connected(),
        }
