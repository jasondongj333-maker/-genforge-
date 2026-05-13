"""
金锤子 (GenForge) - 代码执行器
编译并执行 CAD/Revit 代码
"""
import os
import subprocess
import logging
import tempfile
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Code Executor")


class CodeExecutor:
    """代码执行器"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def execute(self, code, target='autocad'):
        """
        执行代码
        1. 保存代码到临时文件
        2. 编译为 DLL
        3. 发送到 CAD/Revit 执行
        """
        try:
            # 1. 保存代码
            cs_file = self.save_code(code, target)
            dll_file = self.compile_code(cs_file, target)
            
            if not dll_file:
                return {"status": "error", "message": "编译失败"}
            
            # 2. 发送到 CAD 执行
            result = self.send_to_cad(dll_file, target)
            
            return result
            
        except Exception as e:
            logger.error(f"执行错误: {e}")
            return {"status": "error", "message": str(e)}
    
    def save_code(self, code, target):
        """保存代码到临时文件"""
        suffix = f"_{target}.cs"
        filepath = os.path.join(self.temp_dir, f"genforge{suffix}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        logger.info(f"📄 代码已保存: {filepath}")
        return filepath
    
    def compile_code(self, cs_file, target):
        """编译 C# 代码"""
        # 根据目标设置引用
        if target == 'autocad':
            refs = [
                r"C:\Program Files\Autodesk\AutoCAD 2024\acdbmgd.dll",
                r"C:\Program Files\Autodesk\AutoCAD 2024\acmgd.dll"
            ]
        elif target == 'revit':
            # Revit 引用路径（需要安装 Revit SDK）
            refs = [
                r"C:\Program Files\Autodesk\Revit 2024\RevitAPI.dll",
                r"C:\Program Files\Autodesk\Revit 2024\RevitAPIUI.dll"
            ]
        else:
            refs = []
        
        # 输出 DLL
        dll_file = cs_file.replace('.cs', '.dll')
        
        # 构建编译命令
        ref_args = []
        for ref in refs:
            if os.path.exists(ref):
                ref_args.extend(['/r:', f'"{ref}"'])
        
        # 简化：返回 None 表示编译跳过（需要 MSBuild）
        logger.warning("⚠️ 需要 MSBuild 才能编译 C# 代码")
        logger.info(f"代码文件: {cs_file}")
        logger.info(f"引用: {refs}")
        
        return None  # 暂时跳过编译
    
    def send_to_cad(self, dll_file, target):
        """发送到 CAD 执行"""
        # 通过 MCP 或直接调用
        logger.info(f"📤 发送到 {target}: {dll_file}")
        
        return {
            "status": "pending",
            "message": f"代码已生成，等待发送到 {target}",
            "dll_path": dll_file,
            "target": target
        }


class CodeGenerator:
    """代码生成器基类"""
    
    def __init__(self):
        self.template = """
using System;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;

namespace GenForge
{
    public class Commands : IExtensionApplication
    {
        public void Initialize()
        {
            // 插件初始化
        }
        
        public void Terminate()
        {
            // 插件卸载
        }
        
        // 在此添加命令
        {commands}
    }
}
"""
    
    def generate(self, intent_data):
        """生成代码"""
        raise NotImplementedError


class AutoCADCodeGenerator(CodeGenerator):
    """AutoCAD 代码生成器"""
    
    def generate_wall(self, params):
        """生成墙体"""
        width = params.get('width', 1000)  # mm
        height = params.get('height', 2800)  # mm
        length = params.get('length', 5000)  # mm
        
        return f"""
        [CommandMethod("GenForge_Wall")]
        public static void CreateWall()
        {{
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                BlockTable bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                BlockTableRecord btr = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                
                // 创建墙体
                Polyline wall = new Polyline();
                wall.AddVertexAt(0, new Point2d(0, 0), 0, 0, 0);
                wall.AddVertexAt(1, new Point2d({length}, 0), 0, 0, 0);
                wall.AddVertexAt(2, new Point2d({length}, {width}), 0, 0, 0);
                wall.AddVertexAt(3, new Point2d(0, {width}), 0, 0, 0);
                wall.Closed = true;
                
                btr.AppendEntity(wall);
                tr.AddNewlyCreatedDBObject(wall, true);
                
                tr.Commit();
            }}
        }}
        """
    
    def generate_column(self, params):
        """生成柱子"""
        size = params.get('size', 400)  # mm
        height = params.get('height', 2800)  # mm
        
        return f"""
        [CommandMethod("GenForge_Column")]
        public static void CreateColumn()
        {{
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                BlockTable bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                BlockTableRecord btr = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                
                // 创建方形柱子
                Polyline column = new Polyline();
                double half = {size} / 2.0;
                column.AddVertexAt(0, new Point2d(-half, -half), 0, 0, 0);
                column.AddVertexAt(1, new Point2d(half, -half), 0, 0, 0);
                column.AddVertexAt(2, new Point2d(half, half), 0, 0, 0);
                column.AddVertexAt(3, new Point2d(-half, half), 0, 0, 0);
                column.Closed = true;
                
                btr.AppendEntity(column);
                tr.AddNewlyCreatedDBObject(column, true);
                
                tr.Commit();
            }}
        }}
        """
    
    def generate(self, params, command_type='wall'):
        """生成完整代码"""
        if command_type == 'wall':
            commands = self.generate_wall(params)
        elif command_type == 'column':
            commands = self.generate_column(params)
        else:
            commands = "// 未知的命令类型"
        
        return self.template.format(commands=commands)


class RevitCodeGenerator(CodeGenerator):
    """Revit 代码生成器"""
    
    def generate_wall(self, params):
        """生成墙体"""
        width = params.get('width', 1000)
        height = params.get('height', 2800)
        length = params.get('length', 5000)
        
        return f"""
        [Transaction(TransactionMode.Manual)]
        public void CreateWall()
        {{
            Document doc = this.ActiveDocument;
            XYZ start = new XYZ(0, 0, 0);
            XYZ end = new XYZ({length}/304.8, 0, 0);
            
            Wall.Create(doc, start, end, {height}/304.8);
        }}
        """
    
    def generate(self, params, command_type='wall'):
        """生成完整代码"""
        commands = self.generate_wall(params)
        return self.template.format(commands=commands)


class ModelCodeGenerator:
    """模型代码生成器 - 根据意图生成"""
    
    def __init__(self):
        self.cad_generator = AutoCADCodeGenerator()
        self.revit_generator = RevitCodeGenerator()
    
    def generate(self, params, target='autocad'):
        """根据参数生成代码"""
        command_type = params.get('type', 'wall')
        
        if target == 'autocad':
            code = self.cad_generator.generate(params, command_type)
        elif target == 'revit':
            code = self.revit_generator.generate(params, command_type)
        else:
            code = "// 不支持的目标平台"
        
        return code
