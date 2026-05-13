# 墙体绘制标准与规约

## 1. 墙体图层标准

| 图层名 | 用途 | 颜色 | 线宽 |
|--------|------|------|------|
| A-WALL | 墙体轮廓线 | 白色(7) | 0.30mm |

## 2. 墙体厚度规范

| 墙体类型 | 厚度（mm） |
|----------|-----------|
| 外墙（砖混） | 240 |
| 外墙（框架填充） | 200 |
| 内承重墙 | 200 |
| 内隔墙 | 100-120 |
| 卫生间隔墙 | 100 |

## 3. 双线墙绘制模式

```csharp
// 水平方向墙体：从(startX, startY)到(endX, startY)，厚度向上偏移
private void DrawWallSegment(BlockTableRecord btr, Transaction tr,
    double startX, double startY, double endX, double endY,
    double thickness, string layer = "A-WALL")
{
    // 计算法向偏移
    Vector2d dir = new Vector2d(endX - startX, endY - startY).GetNormal();
    Vector2d normal = new Vector2d(-dir.Y, dir.X); // 法向量

    Point3d p1 = new Point3d(startX, startY, 0);
    Point3d p2 = new Point3d(endX, endY, 0);
    Point3d p3 = new Point3d(endX + normal.X * thickness, endY + normal.Y * thickness, 0);
    Point3d p4 = new Point3d(startX + normal.X * thickness, startY + normal.Y * thickness, 0);

    // 外侧线
    Line line1 = new Line(p1, p2); line1.Layer = layer;
    btr.AppendEntity(line1); tr.AddNewlyCreatedDBObject(line1, true);

    // 内侧线
    Line line2 = new Line(p4, p3); line2.Layer = layer;
    btr.AppendEntity(line2); tr.AddNewlyCreatedDBObject(line2, true);
}
```

## 4. 墙体端头封口

外墙转角和墙端头必须用短线段封口，形成封闭腔体：

```csharp
// 封口线段
Line cap = new Line(p1, p4); cap.Layer = "A-WALL";
btr.AppendEntity(cap); tr.AddNewlyCreatedDBObject(cap, true);
```

## 5. 内外墙优先级

1. 先绘制外墙（形成整体轮廓）
2. 再绘制内承重墙
3. 最后绘制内隔墙
4. 门窗洞口需在对应墙线上开口（删除该段）
