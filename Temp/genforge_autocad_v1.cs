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

                // 1. 创建图层 A-WALL（白色，颜色索引7）
                EnsureLayer(db, tr, "A-WALL", 7);

                // 2. 绘制外墙：从 (0,0) 到 (3000,0)，厚度 240mm
                // 下边线
                Line wallBottom = new Line(new Point3d(0, 0, 0), new Point3d(3000, 0, 0));
                wallBottom.Layer = "A-WALL";
                btr.AppendEntity(wallBottom);
                tr.AddNewlyCreatedDBObject(wallBottom, true);
                successCount++;

                // 上边线
                Line wallTop = new Line(new Point3d(0, 240, 0), new Point3d(3000, 240, 0));
                wallTop.Layer = "A-WALL";
                btr.AppendEntity(wallTop);
                tr.AddNewlyCreatedDBObject(wallTop, true);
                successCount++;

                return $"[成功] 完成，处理了 {successCount} 个对象。";
            }
            catch (System.Exception ex)
            {
                return $"[错误] 执行失败：{ex.Message}";
            }
        }

        private void EnsureLayer(Database db, Transaction tr, string layerName, short colorIndex)
        {
            LayerTable lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);
            if (!lt.Has(layerName))
            {
                LayerTableRecord ltr = new LayerTableRecord();
                ltr.Name = layerName;
                ltr.Color = Color.FromColorIndex(ColorMethod.ByAci, colorIndex);
                lt.UpgradeOpen();
                lt.Add(ltr);
                tr.AddNewlyCreatedDBObject(ltr, true);
            }
        }
    }
}