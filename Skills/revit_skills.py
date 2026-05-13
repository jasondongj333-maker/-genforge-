"""
金锤子 (GenForge) - Revit 技能库
"""
from typing import Dict, List, Any


class RevitSkill:
    """Revit 技能基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        raise NotImplementedError
    
    def get_prompt(self) -> str:
        """获取技能描述"""
        return f"{self.name}: {self.description}"


class CreateWallRevitSkill(RevitSkill):
    """Revit 创建墙体"""
    
    def __init__(self):
        super().__init__(
            name="创建墙体",
            description="在 Revit 中创建建筑墙体"
        )
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        width = params.get('width', 6000)  # mm
        height = params.get('height', 2800)  # mm
        thickness = params.get('thickness', 200)  # mm
        
        code = f"""
        [Transaction(TransactionMode.Manual)]
        public class CreateWallCommand : IExternalCommand
        {{
            public Result Execute(
                ExternalCommandData commandData,
                ref string message,
                ElementSet elements)
            {{
                UIDocument uidoc = commandData.Application.ActiveUIDocument;
                Document doc = uidoc.Document;
                
                // 墙体参数
                double length = {width} / 304.8;  // 转换为英尺
                double height = {height} / 304.8;
                double thickness = {thickness} / 304.8;
                
                // 获取默认墙体类型
                FilteredElementCollector collector = new FilteredElementCollector(doc);
                WallType wallType = collector.OfClass(typeof(WallType))
                    .FirstElement() as WallType;
                
                // 创建墙体
                using (Transaction trans = new Transaction(doc, "创建墙体"))
                {{
                    trans.Start();
                    
                    // 使用 Line 创建墙体
                    XYZ start = new XYZ(0, 0, 0);
                    XYZ end = new XYZ(length, 0, 0);
                    Line line = Line.CreateBound(start, end);
                    
                    Wall.Create(doc, line, wallType.Id, height);
                    
                    trans.Commit();
                }}
                
                TaskDialog.Show("完成", "墙体已创建！");
                return Result.Succeeded;
            }}
        }}
        """
        
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params
        }


class CreateColumnRevitSkill(RevitSkill):
    """Revit 创建柱子"""
    
    def __init__(self):
        super().__init__(
            name="创建柱子",
            description="在 Revit 中创建结构柱"
        )
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        size = params.get('size', 400)  # mm
        height = params.get('height', 2800)  # mm
        level = params.get('level', 1)
        
        code = f"""
        [Transaction(TransactionMode.Manual)]
        public class CreateColumnCommand : IExternalCommand
        {{
            public Result Execute(
                ExternalCommandData commandData,
                ref string message,
                ElementSet elements)
            {{
                UIDocument uidoc = commandData.Application.ActiveUIDocument;
                Document doc = uidoc.Document;
                
                double columnSize = {size} / 304.8;
                double columnHeight = {height} / 304.8;
                
                // 获取标高
                FilteredElementCollector collector = new FilteredElementCollector(doc);
                Level baseLevel = collector.OfClass(typeof(Level))
                    .FirstElement() as Level;
                
                // 获取柱子类型
                FamilySymbol columnType = collector.OfClass(typeof(FamilySymbol))
                    .OfCategory(BuiltInCategory.OST_StructuralColumns)
                    .FirstElement() as FamilySymbol;
                
                if (columnType == null)
                {{
                    message = "未找到柱子类型";
                    return Result.Failed;
                }}
                
                using (Transaction trans = new Transaction(doc, "创建柱子"))
                {{
                    trans.Start();
                    
                    if (!columnType.IsActive)
                        columnType.Activate();
                    
                    FamilyInstance column = doc.Create.NewFamilyInstance(
                        new XYZ(0, 0, 0),
                        columnType,
                        baseLevel,
                        Autodesk.Revit.DB.Structure.StructuralType.Column);
                    
                    // 设置尺寸
                    column.LookupParameter("宽度")?.Set(columnSize);
                    column.LookupParameter("深度")?.Set(columnSize);
                    
                    trans.Commit();
                }}
                
                TaskDialog.Show("完成", "柱子已创建！");
                return Result.Succeeded;
            }}
        }}
        """
        
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params
        }


class CreateFloorRevitSkill(RevitSkill):
    """Revit 创建楼板"""
    
    def __init__(self):
        super().__init__(
            name="创建楼板",
            description="在 Revit 中创建楼板"
        )
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        width = params.get('width', 6000)  # mm
        length = params.get('length', 9000)  # mm
        thickness = params.get('thickness', 120)  # mm
        
        code = f"""
        [Transaction(TransactionMode.Manual)]
        public class CreateFloorCommand : IExternalCommand
        {{
            public Result Execute(
                ExternalCommandData commandData,
                ref string message,
                ElementSet elements)
            {{
                UIDocument uidoc = commandData.Application.ActiveUIDocument;
                Document doc = uidoc.Document;
                
                double width = {width} / 304.8;
                double length = {length} / 304.8;
                double thickness = {thickness} / 304.8;
                
                // 获取标高
                FilteredElementCollector collector = new FilteredElementCollector(doc);
                Level level = collector.OfClass(typeof(Level))
                    .FirstElement() as Level;
                
                // 获取楼板类型
                FloorType floorType = collector.OfClass(typeof(FloorType))
                    .FirstElement() as FloorType;
                
                using (Transaction trans = new Transaction(doc, "创建楼板"))
                {{
                    trans.Start();
                    
                    // 创建楼板边界
                    XYZ p1 = new XYZ(0, 0, 0);
                    XYZ p2 = new XYZ(width, 0, 0);
                    XYZ p3 = new XYZ(width, length, 0);
                    XYZ p4 = new XYZ(0, length, 0);
                    
                    List<XYZ> loop = new List<XYZ> {{ p1, p2, p3, p4, p1 }};
                    CurveArray profile = new CurveArray();
                    
                    for (int i = 0; i < loop.Count - 1; i++)
                    {{
                        profile.Append(Line.CreateBound(loop[i], loop[i + 1]));
                    }}
                    
                    Floor.Create(doc, profile, floorType.Id, level.Id);
                    
                    trans.Commit();
                }}
                
                TaskDialog.Show("完成", "楼板已创建！");
                return Result.Succeeded;
            }}
        }}
        """
        
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params
        }


class CreateStairsRevitSkill(RevitSkill):
    """Revit 创建楼梯"""
    
    def __init__(self):
        super().__init__(
            name="创建楼梯",
            description="在 Revit 中创建楼梯"
        )
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        width = params.get('width', 1200)  # mm
        num_steps = params.get('num_steps', 10)
        riser_height = params.get('riser_height', 162)  # mm
        
        code = f"""
        [Transaction(TransactionMode.Manual)]
        public class CreateStairsCommand : IExternalCommand
        {{
            public Result Execute(
                ExternalCommandData commandData,
                ref string message,
                ElementSet elements)
            {{
                UIDocument uidoc = commandData.Application.ActiveUIDocument;
                Document doc = uidoc.Document;
                
                double stairsWidth = {width} / 304.8;
                int stepNumber = {num_steps};
                double riserHeight = {riser_height} / 304.8;
                
                // 获取标高
                FilteredElementCollector collector = new FilteredElementCollector(doc);
                Level level = collector.OfClass(typeof(Level))
                    .FirstElement() as Level;
                
                using (Transaction trans = new Transaction(doc, "创建楼梯"))
                {{
                    trans.Start();
                    
                    // 计算楼梯尺寸
                    double totalRun = stepNumber * 0.28;  // 踏面 280mm
                    double totalRise = stepNumber * riserHeight;
                    
                    // 创建楼梯
                    StairsEditingArea area = null;
                    double halfWidth = stairsWidth / 2;
                    
                    // 创建楼梯
                    IList<XYZ> stairsRun = new List<XYZ>();
                    for (int i = 0; i <= stepNumber; i++)
                    {{
                        double x = i * 0.28;
                        double y = i * riserHeight;
                        stairsRun.Add(new XYZ(x, halfWidth, y));
                    }}
                    
                    trans.Commit();
                }}
                
                TaskDialog.Show("完成", $"楼梯已创建！共{{stepNumber}}步");
                return Result.Succeeded;
            }}
        }}
        """
        
        return {
            "status": "ready",
            "code": code,
            "skill": self.name,
            "params": params
        }


class RevitSkillLibrary:
    """Revit 技能库"""
    
    def __init__(self):
        self.skills = {
            'create_wall': CreateWallRevitSkill(),
            'create_column': CreateColumnRevitSkill(),
            'create_floor': CreateFloorRevitSkill(),
            'create_stairs': CreateStairsRevitSkill(),
        }
    
    def get_skill(self, name: str) -> RevitSkill:
        """获取技能"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[str]:
        """列出所有技能"""
        return list(self.skills.keys())
    
    def get_all_prompts(self) -> str:
        """获取所有技能描述"""
        prompts = ["可用的 Revit 技能："]
        for skill in self.skills.values():
            prompts.append(f"- {skill.get_prompt()}")
        return "\n".join(prompts)
