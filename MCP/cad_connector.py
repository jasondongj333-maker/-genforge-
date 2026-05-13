"""
金锤子 (GenForge) - CAD 连接器
通过 COM API 直接控制 AutoCAD
"""
import logging
import win32com.client
import pythoncom
import time

logger = logging.getLogger("GenForge.CADConnector")


class CADConnector:
    """CAD 连接器 - COM API"""

    def __init__(self):
        self.acad = None
        self._connected = False

    def connect(self) -> bool:
        """连接到已运行的 AutoCAD 实例"""
        try:
            pythoncom.CoInitialize()
            self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
            self._connected = True
            ver = getattr(self.acad, "Version", "未知版本")
            logger.info(f"✅ 已连接到 AutoCAD ({ver})")
            return True
        except Exception:
            try:
                self.acad = win32com.client.Dispatch("AutoCAD.Application")
                self.acad.Visible = True
                self._connected = True
                logger.info("✅ 已启动新 AutoCAD 实例")
                return True
            except Exception as e:
                logger.error(f"❌ 连接 AutoCAD 失败: {e}")
                self._connected = False
                return False

    def is_connected(self) -> bool:
        """返回当前连接状态"""
        if not self._connected or self.acad is None:
            return False
        try:
            _ = self.acad.Version
            return True
        except Exception:
            self._connected = False
            return False

    def send_command(self, command: str) -> bool:
        """
        向 AutoCAD 发送命令（等同于在命令行输入命令）
        
        示例：
        - send_command("LINE 0,0 1000,1000 ")
        - send_command("CIRCLE 0,0 500 ")
        - send_command("-LAYER N A-WALL C 1 A-WALL ")
        """
        if not self.is_connected():
            logger.error("❌ 未连接 AutoCAD")
            return False
        try:
            self.acad.ActiveDocument.SendCommand(command + "\n")
            logger.info(f"✅ 命令已发送: {command}")
            return True
        except Exception as e:
            logger.error(f"❌ 命令发送失败: {e}")
            return False

    def create_layer(self, layer_name: str, color: int = 7) -> bool:
        """
        创建图层
        
        参数：
        - layer_name: 图层名称（如 "A-WALL"）
        - color: 颜色代码（1=红, 2=黄, 3=绿, 4=青, 5=蓝, 6=品红, 7=白/黑）
        """
        cmd = f'-LAYER N {layer_name} C {color} {layer_name} '
        return self.send_command(cmd)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, layer: str = "0") -> bool:
        """
        绘制直线
        
        示例：draw_line(0, 0, 1000, 1000, "A-AXIS")
        """
        self.send_command(f'-LAYER S {layer} ')
        cmd = f'LINE {x1},{y1} {x2},{y2} '
        return self.send_command(cmd)

    def draw_circle(self, x: float, y: float, radius: float, layer: str = "0") -> bool:
        """绘制圆"""
        self.send_command(f'-LAYER S {layer} ')
        cmd = f'CIRCLE {x},{y} {radius} '
        return self.send_command(cmd)

    def draw_rectangle(self, x1: float, y1: float, x2: float, y2: float, layer: str = "0") -> bool:
        """绘制矩形（多段线）"""
        self.send_command(f'-LAYER S {layer} ')
        cmd = f'PLINE {x1},{y1} {x2},{y1} {x2},{y2} {x1},{y2} CL '
        return self.send_command(cmd)

    def draw_polyline(self, points: list, layer: str = "0") -> bool:
        """
        绘制多段线
        
        参数：
        - points: [(x1,y1), (x2,y2), ...] 点列表
        - layer: 图层名称
        
        示例：draw_polyline([(0,0), (1000,0), (1000,500), (0,500)], "A-WALL")
        """
        if len(points) < 2:
            logger.error("❌ 至少需要 2 个点")
            return False
        
        self.send_command(f'-LAYER S {layer} ')
        
        first_point = points[0]
        cmd = f'PLINE {first_point[0]},{first_point[1]} '
        
        for point in points[1:]:
            cmd += f'{point[0]},{point[1]} '
        
        cmd += ' '
        return self.send_command(cmd)

    def zoom_extents(self) -> bool:
        """缩放到全图"""
        return self.send_command('ZOOM E ')

    def set_current_layer(self, layer_name: str) -> bool:
        """设置当前图层"""
        return self.send_command(f'-LAYER S {layer_name} ')

    # ─────────────────────────────────────────────
    # 以下为旧的 DLL 加载方法（保留兼容）
    # ─────────────────────────────────────────────

    def send_lisp(self, lisp_code: str) -> bool:
        """向 AutoCAD 发送 AutoLISP 命令"""
        if not self.is_connected():
            logger.error("未连接 AutoCAD，无法发送命令")
            return False
        try:
            self.acad.ActiveDocument.SendCommand(lisp_code + "\n")
            return True
        except Exception as e:
            logger.error(f"发送 LISP 失败: {e}")
            return False

    def load_dll(self, dll_path: str) -> bool:
        """通过 NETLOAD 命令加载 .NET DLL"""
        safe_path = dll_path.replace("\\", "/")
        lisp_code = f'(command "NETLOAD" "{safe_path}")'
        logger.info(f"📦 加载 DLL: {safe_path}")
        ok = self.send_lisp(lisp_code)
        if ok:
            time.sleep(0.5)
            self.send_lisp('GFRUN\n')
        return ok

    def execute_command(self, command_name: str) -> bool:
        """执行 AutoCAD 命令"""
        lisp_code = f'(command "{command_name}")'
        logger.info(f"🚀 执行命令: {command_name}")
        return self.send_lisp(lisp_code)

    def run_script(self, script: str) -> bool:
        """运行多行 AutoLISP / 命令脚本"""
        for line in script.strip().splitlines():
            line = line.strip()
            if line:
                if not self.send_lisp(line):
                    return False
        return True

    def get_document_path(self) -> str | None:
        """获取当前活动文档路径"""
        try:
            return self.acad.ActiveDocument.FullName
        except Exception:
            return None
