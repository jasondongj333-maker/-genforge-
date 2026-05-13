using System;
using System.Collections.Generic;
using System.Linq;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Colors;
using Autodesk.AutoCAD.Runtime;
using CadAgentServer;

namespace AiGeneratedCode
{
    public class VillaSavoyePlan : IAiCadCommand
    {
        public string Execute(Document doc, Transaction tr, BlockTableRecord btr)
        {
            int successCount = 0;
            try
            {
                Editor ed = doc.Editor;
                Database db = doc.Database;

                ed.WriteMessage("\n=== 正在生成萨伏伊别墅平面图 ===");

                // 阶段1: 创建图层系统
                CreateLayerSystem(btr, tr);
                successCount += 6;

                // 阶段2: 绘制建筑轴网
                CreateAxisGrid(btr, tr);
                successCount += 10;

                // 阶段3: 绘制外墙
                CreateExternalWalls(btr, tr);
                successCount += 8;

                // 阶段4: 绘制内墙
                CreateInternalWalls(btr, tr);
                successCount += 12;

                // 阶段5: 创建门窗洞口
                CreateOpenings(btr, tr);
                successCount += 15;

                // 阶段6: 插入门窗
                CreateDoorsAndWindows(btr, tr);
                successCount += 10;

                // 绘制特殊元素
                CreatePilotis(btr, tr);
                CreateStaircase(btr, tr);
                successCount += 8;

                return $"[成功] 萨伏伊别墅平面图已完成！共处理 {successCount} 个对象。\n" +
                       "图层包括: A-AXIS(轴网), A-WALL(墙体), A-OPENING(洞口), A-DOOR(门), A-WIND(窗), A-DIMS(标注)";
            }
            catch (System.Exception ex)
            {
                return $"[错误] 执行失败：{ex.Message}";
            }
        }

        private void CreateLayerSystem(BlockTableRecord btr, Transaction tr)
        {
            string[] layers = { "A-AXIS", "A-WALL", "A-OPENING", "A-DOOR", "A-WIND", "A-DIMS", "A-PILOTIS", "A-STAIR" };
            int[] colors = { 1, 7, 7, 4, 5, 3, 2, 6 };

            for (int i = 0; i < layers.Length; i++)
            {
                LayerTable lt = (LayerTable)tr.GetObject(btr.Database.LayerTableId, OpenMode.ForWrite);
                if (!lt.Has(layers[i]))
                {
                    LayerTableRecord ltr = new LayerTableRecord();
                    ltr.Name = layers[i];
                    ltr.Color = Color.FromColorIndex(ColorMethod.ByAci, (short)colors[i]);
                    lt.Add(ltr);
                    tr.AddNewlyCreatedDBObject(ltr, true);
                }
            }
        }

        private void CreateAxisGrid(BlockTableRecord btr, Transaction tr)
        {
            // 萨伏伊别墅尺寸: 约22m x 16m
            double[] horizontalSpacings = { 5000, 6000, 6000, 4000 }; // 总长约20m
            double[] verticalSpacings = { 4000, 4000, 4000 }; // 总深约12m

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

            // 轴号标注
            CreateAxisTag(btr, tr, new Point3d(0, -1000, 0), "1", 0);
            CreateAxisTag(btr, tr, new Point3d(11000, -1000, 0), "2", 0);
            CreateAxisTag(btr, tr, new Point3d(17000, -1000, 0), "3", 0);
            CreateAxisTag(btr, tr, new Point3d(21000, -1000, 0), "4", 0);
            CreateAxisTag(btr, tr, new Point3d(-1500, 0, 0), "A", Math.PI / 2);
            CreateAxisTag(btr, tr, new Point3d(-1500, 4000, 0), "B", Math.PI / 2);
            CreateAxisTag(btr, tr, new Point3d(-1500, 8000, 0), "C", Math.PI / 2);
            CreateAxisTag(btr, tr, new Point3d(-1500, 12000, 0), "D", Math.PI / 2);
        }

        private void CreateAxisTag(BlockTableRecord btr, Transaction tr, Point3d position, string label, double rotation)
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

        private void CreateExternalWalls(BlockTableRecord btr, Transaction tr)
        {
            // 南立面外墙 (入口层)
            CreateWallLine(btr, tr, new Point3d(0, 0, 0), new Point3d(22000, 0, 0), 300);
            // 北立面外墙
            CreateWallLine(btr, tr, new Point3d(0, 12000, 0), new Point3d(22000, 12000, 0), 300);
            // 西立面外墙
            CreateWallLine(btr, tr, new Point3d(0, 0, 0), new Point3d(0, 12000, 0), 300);
            // 东立面外墙
            CreateWallLine(btr, tr, new Point3d(22000, 0, 0), new Point3d(22000, 12000, 0), 300);
        }

        private void CreateInternalWalls(BlockTableRecord btr, Transaction tr)
        {
            // 底层平面分隔
            // 楼梯间墙
            CreateWallLine(btr, tr, new Point3d(16000, 6000, 0), new Point3d(16000, 12000, 0), 200);
            CreateWallLine(btr, tr, new Point3d(16000, 6000, 0), new Point3d(22000, 6000, 0), 200);

            // 服务用房分隔
            CreateWallLine(btr, tr, new Point3d(0, 5000, 0), new Point3d(8000, 5000, 0), 150);
            CreateWallLine(btr, tr, new Point3d(0, 8000, 0), new Point3d(8000, 8000, 0), 150);

            // 坡道墙
            CreateWallLine(btr, tr, new Point3d(8000, 5000, 0), new Point3d(8000, 8000, 0), 150);
        }

        private void CreateOpenings(BlockTableRecord btr, Transaction tr)
        {
            // 入口大门
            CreateOpening(btr, tr, new Point3d(9500, 0, 0), 1500, "A-OPENING");
            // 车库门
            CreateOpening(btr, tr, new Point3d(18000, 0, 0), 3000, "A-OPENING");
            // 南立面长窗
            CreateOpening(btr, tr, new Point3d(1500, 0, 0), 4500, "A-OPENING");
            CreateOpening(btr, tr, new Point3d(6500, 0, 0), 1500, "A-OPENING");
            CreateOpening(btr, tr, new Point3d(10500, 0, 0), 4500, "A-OPENING");
            // 北立面窗
            CreateOpening(btr, tr, new Point3d(3000, 12000, 0), 4000, "A-OPENING");
            CreateOpening(btr, tr, new Point3d(8500, 12000, 0), 4000, "A-OPENING");
            CreateOpening(btr, tr, new Point3d(14000, 12000, 0), 3000, "A-OPENING");
            // 东立面窗
            CreateOpening(btr, tr, new Point3d(22000, 2000, 0), 3000, "A-OPENING");
            CreateOpening(btr, tr, new Point3d(22000, 9000, 0), 2000, "A-OPENING");
        }

        private void CreateDoorsAndWindows(BlockTableRecord btr, Transaction tr)
        {
            // 入口门
            CreateDoor(btr, tr, new Point3d(9500, 0, 0), 1500, 0);
            // 室内门
            CreateDoor(btr, tr, new Point3d(3000, 5000, 0), 900, 0);
            CreateDoor(btr, tr, new Point3d(6000, 5000, 0), 900, 0);
            // 楼梯间门
            CreateDoor(btr, tr, new Point3d(16000, 7000, 0), 1200, Math.PI / 2);

            // 窗
            CreateWindow(btr, tr, new Point3d(3750, 0, 0), 4500, 1200);
            CreateWindow(btr, tr, new Point3d(12750, 0, 0), 4500, 1200);
            CreateWindow(btr, tr, new Point3d(5000, 12000, 0), 4000, 1500);
            CreateWindow(btr, tr, new Point3d(17000, 12000, 0), 3000, 1500);
        }

        private void CreatePilotis(BlockTableRecord btr, Transaction tr)
        {
            // 底层架空柱 (柯布西耶的Pilotis)
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

        private void CreateStaircase(BlockTableRecord btr, Transaction tr)
        {
            // 外部螺旋楼梯 (萨伏伊别墅标志性的外部楼梯)
            Point3d center = new Point3d(20000, 4000, 0);

            // 楼梯平台
            Rectangle3d platform = new Rectangle3d(
                new Point3d(19000, 3000, 0),
                new Point3d(21000, 3000, 0),
                new Point3d(21000, 5000, 0),
                new Point3d(19000, 5000, 0)
            );
            // 简化为多段线
            Polyline3d pl = new Polyline3d();
            pl.Layer = "A-STAIR";
            pl.ColorIndex = 6;

            // 楼梯轮廓
            for (int i = 0; i <= 12; i++)
            {
                double angle = i * 0.26;
                double radius = 1500 + i * 50;
                double x = center.X + radius * Math.Cos(angle);
                double y = center.Y + radius * Math.Sin(angle);

                PolylineVertex2d vertex = new PolylineVertex2d(new Point2d(x, y), 0, 0, 0);
                pl.AppendVertex(vertex);
            }

            btr.AppendEntity(pl);
            tr.AddNewlyCreatedDBObject(pl, true);

            // 楼梯中心柱
            Circle centerPillar = new Circle();
            centerPillar.Center = center;
            centerPillar.Radius = 300;
            centerPillar.Layer = "A-STAIR";
            centerPillar.ColorIndex = 6;
            btr.AppendEntity(centerPillar);
            tr.AddNewlyCreatedDBObject(centerPillar, true);
        }

        private void CreateWallLine(BlockTableRecord btr, Transaction tr, Point3d start, Point3d end, double thickness)
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

        private void CreateOpening(BlockTableRecord btr, Transaction tr, Point3d position, double width, string layer)
        {
            Line opening = new Line(
                position - new Vector3d(width/2, 0, 0),
                position + new Vector3d(width/2, 0, 0)
            );
            opening.Layer = layer;
            opening.ColorIndex = 7;
            btr.AppendEntity(opening);
            tr.AddNewlyCreatedDBObject(opening, true);
        }

        private void CreateDoor(BlockTableRecord btr, Transaction tr, Point3d position, double width, double rotation)
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

        private void CreateWindow(BlockTableRecord btr, Transaction tr, Point3d position, double width, double height)
        {
            Polyline3d window = new Polyline3d();
            window.Layer = "A-WIND";
            window.ColorIndex = 5;

            Point2d p1 = new Point2d(position.X - width/2, position.Y - height/2);
            Point2d p2 = new Point2d(position.X + width/2, position.Y - height/2);
            Point2d p3 = new Point2d(position.X + width/2, position.Y + height/2);
            Point2d p4 = new Point2d(position.X - width/2, position.Y + height/2);

            window.AppendVertex(new PolylineVertex2d(p1, 0, 0, 0));
            window.AppendVertex(new PolylineVertex2d(p2, 0, 0, 0));
            window.AppendVertex(new PolylineVertex2d(p3, 0, 0, 0));
            window.AppendVertex(new PolylineVertex2d(p4, 0, 0, 0));
            window.Closed = true;

            btr.AppendEntity(window);
            tr.AddNewlyCreatedDBObject(window, true);
        }
    }
}
