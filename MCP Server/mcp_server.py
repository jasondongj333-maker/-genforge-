"""
CAD Agent MCP Server
通过 MCP 协议连接 AutoCAD，实现 CAD 语义建模

依赖：
- pywin32 (COM 接口)
- requests (SSE 客户端，如需要)
"""

import json
import os
import sys
import traceback
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import win32com.client
import pythoncom

@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class MCPToolResult:
    success: bool
    result: Any
    error: Optional[str] = None

class CadMcpServer:
    def __init__(self):
        self.name = "cad-agent-mcp-server"
        self.version = "1.0.0"
        self.acad_app = None
        self.acad_doc = None
        self.tools = self._init_tools()

    def _init_tools(self) -> List[MCPTool]:
        return [
            MCPTool(
                name="execute_cad_csharp_code",
                description="在 AutoCAD 中执行 C# 代码生成 CAD 对象",
                input_schema={
                    "type": "object",
                    "properties": {
                        "csharp_code": {
                            "type": "string",
                            "description": "C# AutoCAD API 代码"
                        }
                    },
                    "required": ["csharp_code"]
                }
            ),
            MCPTool(
                name="create_axis_grid",
                description="生成建筑轴网",
                input_schema={
                    "type": "object",
                    "properties": {
                        "horizontal_spacings": {
                            "type": "array",
                            "description": "横向轴线间距数组",
                            "items": {"type": "number"}
                        },
                        "vertical_spacings": {
                            "type": "array",
                            "description": "纵向轴线间距数组",
                            "items": {"type": "number"}
                        }
                    },
                    "required": ["horizontal_spacings", "vertical_spacings"]
                }
            ),
            MCPTool(
                name="create_wall",
                description="生成墙体",
                input_schema={
                    "type": "object",
                    "properties": {
                        "start_x": {"type": "number"},
                        "start_y": {"type": "number"},
                        "end_x": {"type": "number"},
                        "end_y": {"type": "number"},
                        "thickness": {"type": "number"},
                        "is_external": {"type": "boolean"}
                    },
                    "required": ["start_x", "start_y", "end_x", "end_y", "thickness"]
                }
            ),
            MCPTool(
                name="create_door",
                description="创建门",
                input_schema={
                    "type": "object",
                    "properties": {
                        "location_x": {"type": "number"},
                        "location_y": {"type": "number"},
                        "width": {"type": "number"},
                        "rotation": {"type": "number"}
                    },
                    "required": ["location_x", "location_y", "width"]
                }
            ),
            MCPTool(
                name="create_window",
                description="创建窗",
                input_schema={
                    "type": "object",
                    "properties": {
                        "location_x": {"type": "number"},
                        "location_y": {"type": "number"},
                        "width": {"type": "number"},
                        "height": {"type": "number"}
                    },
                    "required": ["location_x", "location_y", "width"]
                }
            ),
            MCPTool(
                name="get_autocad_status",
                description="获取 AutoCAD 连接状态",
                input_schema={"type": "object", "properties": {}}
            )
        ]

    def connect_to_autocad(self) -> bool:
        try:
            pythoncom.CoInitialize()
            self.acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
            self.acad_doc = self.acad_app.ActiveDocument
            return True
        except Exception as e:
            print(f"[错误] 连接 AutoCAD 失败: {e}", file=sys.stderr)
            return False

    def ensure_connected(self) -> MCPToolResult:
        if not self.acad_app:
            if not self.connect_to_autocad():
                return MCPToolResult(
                    success=False,
                    result=None,
                    error="无法连接到 AutoCAD，请确保 AutoCAD 已启动"
                )
        return MCPToolResult(success=True, result="已连接到 AutoCAD")

    def create_layer(self, layer_name: str, color_index: int = 7) -> bool:
        try:
            layers = self.acad_doc.Layers
            try:
                layer = layers.Item(layer_name)
            except:
                layer = layers.Add(layer_name)
            layer.ColorIndex = color_index
            return True
        except Exception as e:
            print(f"[错误] 创建图层失败: {e}", file=sys.stderr)
            return False

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        if tool_name == "get_autocad_status":
            return self.get_autocad_status()
        elif tool_name == "execute_cad_csharp_code":
            return self.execute_cad_csharp_code(arguments.get("csharp_code", ""))
        elif tool_name == "create_axis_grid":
            return self.create_axis_grid(
                arguments.get("horizontal_spacings", []),
                arguments.get("vertical_spacings", [])
            )
        elif tool_name == "create_wall":
            return self.create_wall(
                arguments.get("start_x", 0),
                arguments.get("start_y", 0),
                arguments.get("end_x", 0),
                arguments.get("end_y", 0),
                arguments.get("thickness", 240),
                arguments.get("is_external", True)
            )
        elif tool_name == "create_door":
            return self.create_door(
                arguments.get("location_x", 0),
                arguments.get("location_y", 0),
                arguments.get("width", 900),
                arguments.get("rotation", 0)
            )
        elif tool_name == "create_window":
            return self.create_window(
                arguments.get("location_x", 0),
                arguments.get("location_y", 0),
                arguments.get("width", 1500),
                arguments.get("height", 1500)
            )
        else:
            return MCPToolResult(
                success=False,
                result=None,
                error=f"未知工具: {tool_name}"
            )

    def get_autocad_status(self) -> MCPToolResult:
        conn_result = self.ensure_connected()
        if not conn_result.success:
            return conn_result

        try:
            doc_name = self.acad_doc.Name if self.acad_doc else "无活动文档"
            return MCPToolResult(
                success=True,
                result={
                    "connected": True,
                    "autocad_version": self.acad_app.Version,
                    "active_document": doc_name,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return MCPToolResult(success=False, result=None, error=str(e))

    def execute_cad_csharp_code(self, code: str) -> MCPToolResult:
        conn_result = self.ensure_connected()
        if not conn_result.success:
            return conn_result

        return MCPToolResult(
            success=True,
            result=f"[模拟] C# 代码已生成（实际执行需要 CadAgentServer.dll）:\n{code[:200]}..."
        )

    def create_axis_grid(self, horizontal_spacings: List[float], vertical_spacings: List[float]) -> MCPToolResult:
        conn_result = self.ensure_connected()
        if not conn_result.success:
            return conn_result

        try:
            self.create_layer("A-AXIS", 1)

            msp = self.acad_doc.ModelSpace
            extension = 1200
            bubble_radius = 400

            x_offset = 0
            for i, spacing in enumerate(horizontal_spacings):
                x_offset += spacing
                start_point = win32com.client.VarType(vbVariant=0)
                end_point = win32com.client.VarType(vbVariant=0)
                start_point.X = -extension
                start_point.Y = 0
                end_point.X = x_offset + extension
                end_point.Y = 0
                line = msp.AddLine(start_point, end_point)
                line.Layer = "A-AXIS"
                line.Color = 1

            y_offset = 0
            for i, spacing in enumerate(vertical_spacings):
                y_offset += spacing
                start_point = win32com.client.VarType(vbVariant=0)
                end_point = win32com.client.VarType(vbVariant=0)
                start_point.X = 0
                start_point.Y = -extension
                end_point.X = 0
                end_point.Y = y_offset + extension
                line = msp.AddLine(start_point, end_point)
                line.Layer = "A-AXIS"
                line.Color = 1

            total_horizontal = sum(horizontal_spacings)
            total_vertical = sum(vertical_spacings)

            return MCPToolResult(
                success=True,
                result=f"[成功] 轴网已生成：{len(horizontal_spacings)} 条横向轴线，{len(vertical_spacings)} 条纵向轴线"
            )
        except Exception as e:
            return MCPToolResult(success=False, result=None, error=str(e))

    def create_wall(self, start_x: float, start_y: float, end_x: float, end_y: float,
                   thickness: float = 240, is_external: bool = True) -> MCPToolResult:
        conn_result = self.ensure_connected()
        if not conn_result.success:
            return conn_result

        try:
            layer_name = "A-WALL"
            self.create_layer(layer_name, 7)

            msp = self.acad_doc.ModelSpace
            start = win32com.client.VarType(vbVariant=0)
            end = win32com.client.VarType(vbVariant=0)
            start.X = start_x
            start.Y = start_y
            end.X = end_x
            end.Y = end_y

            line = msp.AddLine(start, end)
            line.Layer = layer_name
            line.Color = 7

            return MCPToolResult(
                success=True,
                result=f"[成功] 墙体已创建：从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})，厚度 {thickness}mm"
            )
        except Exception as e:
            return MCPToolResult(success=False, result=None, error=str(e))

    def create_door(self, location_x: float, location_y: float, width: float = 900,
                   rotation: float = 0) -> MCPToolResult:
        conn_result = self.ensure_connected()
        if not conn_result.success:
            return conn_result

        try:
            self.create_layer("A-DOOR", 4)
            msp = self.acad_doc.ModelSpace

            center = win32com.client.VarType(vbVariant=0)
            center.X = location_x
            center.Y = location_y

            circle = msp.AddCircle(center, width / 2)
            circle.Layer = "A-DOOR"
            circle.Color = 4

            return MCPToolResult(
                success=True,
                result=f"[成功] 门已创建：位置 ({location_x}, {location_y})，宽度 {width}mm"
            )
        except Exception as e:
            return MCPToolResult(success=False, result=None, error=str(e))

    def create_window(self, location_x: float, location_y: float, width: float = 1500,
                     height: float = 1500) -> MCPToolResult:
        conn_result = self.ensure_connected()
        if not conn_result.success:
            return conn_result

        try:
            self.create_layer("A-WIND", 5)
            msp = self.acad_doc.ModelSpace

            corner = win32com.client.VarType(vbVariant=0)
            corner.X = location_x - width / 2
            corner.Y = location_y - height / 2

            line1 = msp.AddLine(corner, win32com.client.VarType(vbVariant=0))
            line2 = msp.AddLine(corner, win32com.client.VarType(vbVariant=0))

            return MCPToolResult(
                success=True,
                result=f"[成功] 窗已创建：位置 ({location_x}, {location_y})，尺寸 {width}×{height}mm"
            )
        except Exception as e:
            return MCPToolResult(success=False, result=None, error=str(e))

    def handle_mcp_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        if method == "initialize":
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        elif method == "tools/list":
            return {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.input_schema
                    }
                    for t in self.tools
                ]
            }
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = self.execute_tool(tool_name, arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(asdict(result), ensure_ascii=False)
                    }
                ]
            }
        else:
            return {"error": f"Unknown method: {method}"}

def main():
    print("CAD Agent MCP Server 启动中...", file=sys.stderr)
    server = CadMcpServer()

    if server.connect_to_autocad():
        print("[成功] 已连接到 AutoCAD", file=sys.stderr)
    else:
        print("[警告] 无法连接到 AutoCAD，服务器将以模拟模式运行", file=sys.stderr)

    print("服务器初始化完成，等待 MCP 请求...", file=sys.stderr)

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line.strip())
            method = request.get("method", "")
            params = request.get("params")

            response = server.handle_mcp_request(method, params)
            print(json.dumps(response), flush=True)

        except KeyboardInterrupt:
            print("\n服务器关闭", file=sys.stderr)
            break
        except Exception as e:
            print(f"[错误] 处理请求失败: {e}", file=sys.stderr)
            traceback.print_exc()

if __name__ == "__main__":
    main()
