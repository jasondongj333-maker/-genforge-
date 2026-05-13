"""
金锤子 (GenForge) - CAD 技能库
"""
from typing import Dict, List, Any


class CADSkill:
    """CAD 技能基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        raise NotImplementedError

    def get_prompt(self) -> str:
        """获取技能描述"""
        return f"{self.name}: {self.description}"


class CreateLayerSkill(CADSkill):
    """创建图层"""

    def __init__(self):
        super().__init__(
            name="创建图层",
            description="在 AutoCAD 中创建新图层"
        )

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        layer_name = params.get('layer_name', 'NewLayer')
        color = params.get('color', 7)

        code = f'''
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Colors;

namespace GenForge
{{
    public class Commands
    {{
        [CommandMethod("GenForge_CreateLayer")]
        public static void CreateLayer()
        {{
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            Editor ed = doc.Editor;
            
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                LayerTable lt = tr.GetObject(db.LayerTableId, OpenMode.ForRead) as LayerTable;
                
                if (!lt.Has("{layer_name}"))
                {{
                    LayerTableRecord ltr = new LayerTableRecord();
                    ltr.Name = "{layer_name}";
                    ltr.Color = Color.FromColorIndex(ColorMethod.ByAci, {color});
                    
                    lt.UpgradeOpen();
                    lt.Add(ltr);
                    tr.AddNewlyCreatedDBObject(ltr, true);
                    
                    ed.WriteMessage("图层 {layer_name} 创建成功！\\n");
                }}
                else
                {{
                    ed.WriteMessage("图层 {layer_name} 已存在！\\n");
                }}
                
                tr.Commit();
            }}
        }}
    }}
}}
'''
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params,
            "command": "GenForge_CreateLayer"
        }


class DrawWallSkill(CADSkill):
    """绘制墙体"""

    def __init__(self):
        super().__init__(
            name="绘制墙体",
            description="在 AutoCAD 中绘制墙体"
        )

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        layer = params.get('layer', 'WALL')
        thickness = params.get('thickness', 200)
        height = params.get('height', 2800)

        code = f'''
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Colors;

namespace GenForge
{{
    public class Commands
    {{
        [CommandMethod("GenForge_DrawWall")]
        public static void DrawWall()
        {{
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            Editor ed = doc.Editor;
            
            // 创建图层（如果不存在）
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                LayerTable lt = tr.GetObject(db.LayerTableId, OpenMode.ForRead) as LayerTable;
                
                if (!lt.Has("{layer}"))
                {{
                    LayerTableRecord ltr = new LayerTableRecord();
                    ltr.Name = "{layer}";
                    ltr.Color = Color.FromColorIndex(ColorMethod.ByAci, 2); // 红色
                    
                    lt.UpgradeOpen();
                    lt.Add(ltr);
                    tr.AddNewlyCreatedDBObject(ltr, true);
                }}
                
                tr.Commit();
            }}
            
            // 绘制墙体（两条平行线表示厚度）
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                BlockTable bt = tr.GetObject(db.BlockTableId, OpenMode.ForRead) as BlockTable;
                BlockTableRecord btr = tr.GetObject(bt[BlockTableRecord.ModelSpace], 
                                                    OpenMode.ForWrite) as BlockTableRecord;
                
                // 绘制墙体线（从原点开始画一条10米长的墙）
                Line wallLine1 = new Line(new Point3d(0, 0, 0), new Point3d(10000, 0, 0));
                wallLine1.Layer = "{layer}";
                wallLine1.LineWeight = LineWeight.LineWeight030; // 粗线
                
                Line wallLine2 = new Line(new Point3d(0, {thickness}, 0), new Point3d(10000, {thickness}, 0));
                wallLine2.Layer = "{layer}";
                wallLine2.LineWeight = LineWeight.LineWeight030;
                
                btr.AppendEntity(wallLine1);
                tr.AddNewlyCreatedDBObject(wallLine1, true);
                
                btr.AppendEntity(wallLine2);
                tr.AddNewlyCreatedDBObject(wallLine2, true);
                
                ed.WriteMessage("墙体绘制成功！\\n");
                ed.WriteMessage("图层: {layer}, 厚度: {thickness}mm, 高度: {height}mm\\n");
                
                tr.Commit();
            }}
        }}
    }}
}}
'''
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params,
            "command": "GenForge_DrawWall"
        }


class DrawDoorSkill(CADSkill):
    """绘制门"""

    def __init__(self):
        super().__init__(
            name="绘制门",
            description="在 AutoCAD 中绘制门"
        )

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        width = params.get('width', 900)
        height = params.get('height', 2100)

        code = f'''
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Colors;

namespace GenForge
{{
    public class Commands
    {{
        [CommandMethod("GenForge_DrawDoor")]
        public static void DrawDoor()
        {{
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            Editor ed = doc.Editor;
            
            // 创建门图层
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                LayerTable lt = tr.GetObject(db.LayerTableId, OpenMode.ForRead) as LayerTable;
                
                if (!lt.Has("DOOR"))
                {{
                    LayerTableRecord ltr = new LayerTableRecord();
                    ltr.Name = "DOOR";
                    ltr.Color = Color.FromColorIndex(ColorMethod.ByAci, 3); // 绿色
                    
                    lt.UpgradeOpen();
                    lt.Add(ltr);
                    tr.AddNewlyCreatedDBObject(ltr, true);
                }}
                
                tr.Commit();
            }}
            
            // 绘制门（简单表示）
            using (Transaction tr = db.TransactionManager.StartTransaction())
            {{
                BlockTable bt = tr.GetObject(db.BlockTableId, OpenMode.ForRead) as BlockTable;
                BlockTableRecord btr = tr.GetObject(bt[BlockTableRecord.ModelSpace], 
                                                    OpenMode.ForWrite) as BlockTableRecord;
                
                int width = {width};
                int height = {height};
                
                // 绘制门的矩形表示
                Polyline door = new Polyline();
                door.AddVertexAt(0, new Point2d(0, 0), 0, 0, 0);
                door.AddVertexAt(1, new Point2d(width, 0), 0, 0, 0);
                door.AddVertexAt(2, new Point2d(width, height), 0, 0, 0);
                door.AddVertexAt(3, new Point2d(0, height), 0, 0, 0);
                door.Closed = true;
                door.Layer = "DOOR";
                
                btr.AppendEntity(door);
                tr.AddNewlyCreatedDBObject(door, true);
                
                ed.WriteMessage("门绘制成功！\\n");
                ed.WriteMessage("宽度: {width}mm, 高度: {height}mm\\n");
                
                tr.Commit();
            }}
        }}
    }}
}}
'''
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params,
            "command": "GenForge_DrawDoor"
        }


class CADSkillLibrary:
    """CAD 技能库"""

    def __init__(self):
        self.skills = {
            'create_layer': CreateLayerSkill(),
            'draw_wall': DrawWallSkill(),
            'draw_door': DrawDoorSkill(),
        }

    def get_skill(self, name: str) -> CADSkill:
        """获取技能"""
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        """列出所有技能"""
        return list(self.skills.keys())

    def get_all_prompts(self) -> str:
        """获取所有技能描述"""
        prompts = ["可用的 CAD 技能："]
        for skill in self.skills.values():
            prompts.append(f"- {skill.get_prompt()}")
        return "\n".join(prompts)
