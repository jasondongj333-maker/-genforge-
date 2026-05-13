/// ============================================
/// 萨伏伊别墅平面图 - 独立 C# 源码
/// ============================================

using System;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Colors;
using Autodesk.AutoCAD.Runtime;

namespace VillaSavoye
{
    public class VillaSavoyeCommands
    {
        [CommandMethod("DrawVillaSavoye")]
        public static void DrawVillaSavoyeCommand()
        {
            Document doc = Application.DocumentManager.MdiActiveDocument;
            Database db = doc.Database;
            Editor ed = doc.Editor;

            ed.WriteMessage("\n=== 正在生成萨伏伊别墅平面图 ===\n");

            using (Transaction tr = db.TransactionManager.StartTransaction())
            {
                BlockTable bt = tr.GetObject(db.BlockTableId, OpenMode.ForRead) as BlockTable;
                BlockTableRecord btr = tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite) as BlockTableRecord;

                try
                {
                    int count = ExecuteDrawing(btr, tr);
                    tr.Commit();
                    ed.WriteMessage($"\n✅ 完成！共绘制 {count} 个对象\n");
                }
                catch (Exception ex)
                {
                    ed.WriteMessage($"\n❌ 错误: {ex.Message}\n");
                    tr.Abort();
                }
            }
        }

        public static int ExecuteDrawing(BlockTableRecord btr, Transaction tr)
        {
            int successCount = 0;

            CreateLayerSystem(btr.Database, tr);
            successCount += 8;

            CreateAxisGrid(btr, tr);
            successCount += 20;

            CreateExternalWalls(btr, tr);
            successCount += 8;

            CreateInternalWalls(btr, tr);
            successCount += 12;

            CreateOpenings(btr, tr);
            successCount += 10;

            CreateDoorsAndWindows(btr, tr);
            successCount += 10;

            CreatePilotis(btr, tr);
            CreateStaircase(btr, tr);
            successCount += 15;

            return successCount;
        }

        private static void CreateLayerSystem(Database db, Transaction tr)
        {
            LayerTable lt = tr.GetObject(db.LayerTableId, OpenMode.ForWrite) as LayerTable;

            var layers = new[] {
                ("A-AXIS", 1),
                ("A-WALL", 7),
                ("A-OPENING", 7),
                ("A-DOOR", 4),
                ("A-WIND", 5),
                ("A-DIMS", 3),
                ("A-PILOTIS", 2),
                ("A-STAIR", 6)
            };

            foreach (var (name, colorIndex) in layers)
            {
                if (!lt.Has(name))
                {
                    LayerTableRecord ltr = new LayerTableRecord();
                    ltr.Name = name;
                    ltr.Color = Color.FromColorIndex(ColorMethod.ByAci, (short)colorIndex);
                    lt.Add(ltr);
                    tr.AddNewlyCreatedDBObject(ltr, true);
                }
            }
        }

        private static void CreateAxisGrid(BlockTableRecord btr, Transaction tr)
        {
            double[] horizontalSpacings = { 5000, 6000, 6000, 4000 };
            double[] verticalSpacings = { 4000, 4000, 4000 };

            double xOffset = 0;
            for (int i = 0; i < horizontalSpacings.Length; i++)
            {
                xOffset += horizontalSpacings[i];
                Line axisLine = new Line(
                    new Point3d(-1500, -1000, 0),
                    new Point3d(xOffset + 1500, -1000, 0)
                );
                axisLine.Layer = "A-AXIS";
                axisLine.ColorIndex = 1;
                btr.AppendEntity(axisLine);
                tr.AddNewlyCreatedDBObject(axisLine, true);
            }

            double yOffset = 0;
            for (int i = 0; i < verticalSpacings.Length; i++)
            {
                yOffset += verticalSpacings[i];
                Line axisLine = new Line(
                    new Point3d(-1500, -1000, 0),
                    new Point3d(-1500, yOffset + 1500, 0)
                );
                axisLine.Layer = "A-AXIS";
                axisLine.ColorIndex = 1;
                btr.AppendEntity(axisLine);
                tr.AddNewlyCreatedDBObject(axisLine, true);
            }

            CreateAxisTag(btr, tr, new Point3d(0, -1000, 0), "1", 0);
            CreateAxisTag(btr, tr, new Point3d(11000, -1000, 0), "2", 0);
            CreateAxisTag(btr, tr, new Point3d(17000, -1000, 0), "3", 0);
            CreateAxisTag(btr, tr, new Point3d(21000, -1000, 0), "4", 0);
            CreateAxisTag(btr, tr, new Point3d(-1500, 0, 0), "A", Math.PI / 2);
            CreateAxisTag(btr, tr, new Point3d(-1500, 4000, 0), "B", Math.PI / 2);
            CreateAxisTag(btr, tr, new Point3d(-1500, 8000, 0), "C", Math.PI / 2);
            CreateAxisTag(btr, tr, new Point3d(-1500, 12000, 0), "D", Math.PI / 2);
        }

        private static void CreateAxisTag(BlockTableRecord btr, Transaction tr, Point3d position, string label, double rotation)
        {
            Circle bubble = new Circle();
            bubble.Center = position;
            bubble.Radius = 400;
            bubble.Layer = "A-AXIS";
            bubble.ColorIndex = 7;
            btr.AppendEntity(bubble);
            tr.AddNewlyCreatedDBObject(bubble, true);

            DBText text = new DBText();
            text.Contents = label;
            text.Height = 300;
            text.Layer = "A-AXIS";
            text.ColorIndex = 7;
            text.Justify = AttachmentPoint.MiddleCenter;
            text.AlignmentPoint = position;
            text.Rotation = rotation;
            btr.AppendEntity(text);
            tr.AddNewlyCreatedDBObject(text, true);
        }

        private static void CreateExternalWalls(BlockTableRecord btr, Transaction tr)
        {
            CreateWallLine(btr, tr, new Point3d(0, 0, 0), new Point3d(22000, 0, 0), 300);
            CreateWallLine(btr, tr, new Point3d(0, 12000, 0), new Point3d(22000, 12000, 0), 300);
            CreateWallLine(btr, tr, new Point3d(0, 0, 0), new Point3d(0, 12000, 0), 300);
            CreateWallLine(btr, tr, new Point3d(22000, 0, 0), new Point3d(22000, 12000, 0), 300);
        }

        private static void CreateInternalWalls(BlockTableRecord btr, Transaction tr)
        {
            CreateWallLine(btr, tr, new Point3d(16000, 6000, 0), new Point3d(16000, 12000, 0), 200);
            CreateWallLine(btr, tr, new Point3d(16000, 6000, 0), new Point3d(22000, 6000, 0), 200);
            CreateWallLine(btr, tr, new Point3d(0, 5000, 0), new Point3d(8000, 5000, 0), 150);
            CreateWallLine(btr, tr, new Point3d(0, 8000, 0), new Point3d(8000, 8000, 0), 150);
            CreateWallLine(btr, tr, new Point3d(8000, 5000, 0), new Point3d(8000, 8000, 0), 150);
        }

        private static void CreateOpenings(BlockTableRecord btr, Transaction tr)
        {
            CreateOpening(btr, tr, new Point3d(9500, 0, 0), 1500);
            CreateOpening(btr, tr, new Point3d(18000, 0, 0), 3000);
            CreateOpening(btr, tr, new Point3d(1500, 0, 0), 4500);
            CreateOpening(btr, tr, new Point3d(6500, 0, 0), 1500);
            CreateOpening(btr, tr, new Point3d(10500, 0, 0), 4500);
            CreateOpening(btr, tr, new Point3d(3000, 12000, 0), 4000);
            CreateOpening(btr, tr, new Point3d(8500, 12000, 0), 4000);
            CreateOpening(btr, tr, new Point3d(14000, 12000, 0), 3000);
            CreateOpening(btr, tr, new Point3d(22000, 2000, 0), 3000);
            CreateOpening(btr, tr, new Point3d(22000, 9000, 0), 2000);
        }

        private static void CreateDoorsAndWindows(BlockTableRecord btr, Transaction tr)
        {
            CreateDoor(btr, tr, new Point3d(9500, 0, 0), 1500, 0);
            CreateDoor(btr, tr, new Point3d(3000, 5000, 0), 900, 0);
            CreateDoor(btr, tr, new Point3d(6000, 5000, 0), 900, 0);
            CreateDoor(btr, tr, new Point3d(16000, 7000, 0), 1200, Math.PI / 2);
            CreateWindow(btr, tr, new Point3d(3750, 0, 0), 4500, 1200);
            CreateWindow(btr, tr, new Point3d(12750, 0, 0), 4500, 1200);
            CreateWindow(btr, tr, new Point3d(5000, 12000, 0), 4000, 1500);
            CreateWindow(btr, tr, new Point3d(17000, 12000, 0), 3000, 1500);
        }

        private static void CreatePilotis(BlockTableRecord btr, Transaction tr)
        {
            Point3d[] pilotisPositions = {
                new Point3d(2000, 2000, 0),
                new Point3d(2000, 6000, 0),
                new Point3d(2000, 10000, 0),
                new Point3d(6000, 2000, 0),
                new Point3d(6000, 6000, 0),
                new Point3d(6000, 10000, 0),
                new Point3d(10000, 2000, 0),
                new Point3d(10000, 6000, 0),
                new Point3d(10000, 10000, 0),
                new Point3d(14000, 2000, 0),
                new Point3d(14000, 6000, 0),
                new Point3d(18000, 2000, 0)
            };

            foreach (Point3d pos in pilotisPositions)
            {
                Circle pilotis = new Circle();
                pilotis.Center = pos;
                pilotis.Radius = 200;
                pilotis.Layer = "A-PILOTIS";
                pilotis.ColorIndex = 2;
                btr.AppendEntity(pilotis);
                tr.AddNewlyCreatedDBObject(pilotis, true);
            }
        }

        private static void CreateStaircase(BlockTableRecord btr, Transaction tr)
        {
            Point3d center = new Point3d(20000, 4000, 0);

            Circle centerPillar = new Circle();
            centerPillar.Center = center;
            centerPillar.Radius = 300;
            centerPillar.Layer = "A-STAIR";
            centerPillar.ColorIndex = 6;
            btr.AppendEntity(centerPillar);
            tr.AddNewlyCreatedDBObject(centerPillar, true);

            Polyline spiral = new Polyline();
            spiral.Layer = "A-STAIR";
            spiral.ColorIndex = 6;

            for (int i = 0; i <= 24; i++)
            {
                double angle = i * 0.26;
                double radius = 1500 + i * 20;
                double x = center.X + radius * Math.Cos(angle);
                double y = center.Y + radius * Math.Sin(angle);
                spiral.AddVertexAt(i, new Point2d(x, y), 0, 0, 0);
            }

            btr.AppendEntity(spiral);
            tr.AddNewlyCreatedDBObject(spiral, true);
        }

        private static void CreateWallLine(BlockTableRecord btr, Transaction tr, Point3d start, Point3d end, double thickness)
        {
            Vector3d direction = (end - start).GetNormal();
            Vector3d perpendicular = direction.CrossProduct(Vector3d.ZAxis).GetNormal();
            double halfThickness = thickness / 2;

            Line outerLine = new Line(start + perpendicular * halfThickness, end + perpendicular * halfThickness);
            outerLine.Layer = "A-WALL";
            outerLine.ColorIndex = 7;
            btr.AppendEntity(outerLine);
            tr.AddNewlyCreatedDBObject(outerLine, true);

            Line innerLine = new Line(start - perpendicular * halfThickness, end - perpendicular * halfThickness);
            innerLine.Layer = "A-WALL";
            innerLine.ColorIndex = 7;
            btr.AppendEntity(innerLine);
            tr.AddNewlyCreatedDBObject(innerLine, true);
        }

        private static void CreateOpening(BlockTableRecord btr, Transaction tr, Point3d position, double width)
        {
            Line opening = new Line(
                position - new Vector3d(width/2, 0, 0),
                position + new Vector3d(width/2, 0, 0)
            );
            opening.Layer = "A-OPENING";
            opening.ColorIndex = 7;
            btr.AppendEntity(opening);
            tr.AddNewlyCreatedDBObject(opening, true);
        }

        private static void CreateDoor(BlockTableRecord btr, Transaction tr, Point3d position, double width, double rotation)
        {
            Circle doorArc = new Circle();
            doorArc.Center = position;
            doorArc.Radius = width;
            doorArc.Layer = "A-DOOR";
            doorArc.ColorIndex = 4;
            doorArc.Thickness = 50;
            btr.AppendEntity(doorArc);
            tr.AddNewlyCreatedDBObject(doorArc, true);
        }

        private static void CreateWindow(BlockTableRecord btr, Transaction tr, Point3d position, double width, double height)
        {
            Polyline window = new Polyline();
            window.Layer = "A-WIND";
            window.ColorIndex = 5;

            Point2d p1 = new Point2d(position.X - width/2, position.Y - height/2);
            Point2d p2 = new Point2d(position.X + width/2, position.Y - height/2);
            Point2d p3 = new Point2d(position.X + width/2, position.Y + height/2);
            Point2d p4 = new Point2d(position.X - width/2, position.Y + height/2);

            window.AddVertexAt(0, p1, 0, 0, 0);
            window.AddVertexAt(1, p2, 0, 0, 0);
            window.AddVertexAt(2, p3, 0, 0, 0);
            window.AddVertexAt(3, p4, 0, 0, 0);
            window.Closed = true;

            btr.AppendEntity(window);
            tr.AddNewlyCreatedDBObject(window, true);
        }
    }
}
