# 门窗洞口标准与规约

## 1. 图层标准

| 图层名 | 用途 | 颜色 |
|--------|------|------|
| A-DOOR | 门 | 青色(4) |
| A-WIND | 窗 | 天蓝色(5) |
| A-OPENING | 洞口辅助线（临时） | 白色(7) |

## 2. 标准洞口尺寸

### 门洞口
| 类型 | 宽度（mm） | 高度（mm） |
|------|-----------|-----------|
| 入户门 | 1000 | 2100 |
| 卧室门 | 900 | 2100 |
| 卫生间门 | 750-800 | 2000 |
| 厨房门 | 800-900 | 2100 |
| 阳台门 | 900-1000 | 2100 |

### 窗洞口
| 类型 | 宽度（mm） | 高度（mm） | 窗台高（mm） |
|------|-----------|-----------|------------|
| 客厅大窗 | 2400-3600 | 1500-1800 | 900 |
| 卧室窗 | 1500-2100 | 1500 | 900 |
| 厨房窗 | 1200-1500 | 900-1200 | 900 |
| 卫生间高窗 | 600-900 | 600 | 1500-1800 |

## 3. 门的平面图表示（CAD标准）

```csharp
// 门的平面图：门洞 + 门扇弧线
private void DrawDoor(BlockTableRecord btr, Transaction tr,
    Point3d basePoint, double width, int direction = 1)
{
    // 方向: 1=向上开, -1=向下开
    // 门扇矩形（简化表示）
    Line doorLeaf = new Line(basePoint,
        new Point3d(basePoint.X + width, basePoint.Y, 0));
    doorLeaf.Layer = "A-DOOR";
    btr.AppendEntity(doorLeaf); tr.AddNewlyCreatedDBObject(doorLeaf, true);

    // 开启弧（1/4 圆弧）
    Arc arc = new Arc(
        new Point3d(basePoint.X, basePoint.Y, 0),
        width,
        0,
        Math.PI / 2 * direction
    );
    arc.Layer = "A-DOOR";
    btr.AppendEntity(arc); tr.AddNewlyCreatedDBObject(arc, true);
}
```

## 4. 窗的平面图表示（CAD标准）

```csharp
// 窗的平面图：三线表示（外框+玻璃中线）
private void DrawWindow(BlockTableRecord btr, Transaction tr,
    Point3d startPt, Point3d endPt, double wallThickness)
{
    // 外侧线
    Line outer = new Line(startPt, endPt); outer.Layer = "A-WIND";
    btr.AppendEntity(outer); tr.AddNewlyCreatedDBObject(outer, true);

    // 中线（玻璃位置，在墙厚中心）
    double midOffset = wallThickness / 2.0;
    // 假设墙体沿X方向，偏移沿Y方向
    Line middle = new Line(
        new Point3d(startPt.X, startPt.Y + midOffset, 0),
        new Point3d(endPt.X, endPt.Y + midOffset, 0));
    middle.Layer = "A-WIND";
    btr.AppendEntity(middle); tr.AddNewlyCreatedDBObject(middle, true);

    // 内侧线
    Line inner = new Line(
        new Point3d(startPt.X, startPt.Y + wallThickness, 0),
        new Point3d(endPt.X, endPt.Y + wallThickness, 0));
    inner.Layer = "A-WIND";
    btr.AppendEntity(inner); tr.AddNewlyCreatedDBObject(inner, true);
}
```

## 5. 门窗位置规则

- 门窗洞口距墙转角最小净距：≥ 300mm
- 两窗间实墙宽：≥ 500mm
- 门窗不得相互碰撞
