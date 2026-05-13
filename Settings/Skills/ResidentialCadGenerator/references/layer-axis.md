# 建筑轴网生成标准与规约

## 1. 几何规约

- **基准点**：所有轴网生成基于绝对坐标 `(0, 0, 0)`
- **图层**：`A-AXIS`，颜色红色(1)，线型 `CENTER`（点划线）
- **外伸长度**：轴线两端超出最外侧交点 `1000-1500mm`，供放置轴号圆圈

## 2. 轴号标注规范（GB/T 50001）

- **圆圈直径**：模型空间 `800-1000mm`（1:100 出图比例下 8-10mm）
- **横向编号**：从左向右，阿拉伯数字 `1, 2, 3...`
- **纵向编号**：从下向上，大写字母 `A, B, C...`
  - **强制约束**：不得使用 `I`, `O`, `Z`（易与数字混淆）

## 3. 轴号绘制代码模板

```csharp
private void CreateAxisTag(BlockTableRecord btr, Transaction tr, Database db,
    Point3d endPoint, string label, Vector3d direction)
{
    double totalOffset = 1000 + 400; // 外伸 + 半径
    Point3d centerPt = endPoint + (direction * totalOffset);

    // 轴号圆圈
    Circle bubble = new Circle();
    bubble.Center = centerPt;
    bubble.Radius = 400.0;
    bubble.Layer = "A-AXIS";
    bubble.ColorIndex = 7;
    btr.AppendEntity(bubble);
    tr.AddNewlyCreatedDBObject(bubble, true);

    // 轴号文字
    DBText txt = new DBText();
    txt.TextString = label;
    txt.Height = 350.0;
    txt.Layer = "A-TEXT";
    txt.ColorIndex = 3;
    txt.Justify = AttachmentPoint.MiddleCenter;
    txt.AlignmentPoint = centerPt;
    txt.AdjustAlignment(db);
    btr.AppendEntity(txt);
    tr.AddNewlyCreatedDBObject(txt, true);
}
```

## 4. 轴网数据结构

```json
{
  "horizontal_spacings": [3900, 4200, 3300],
  "vertical_spacings": [6000, 6000],
  "bubble_radius": 400,
  "extension_length": 1200
}
```

## 5. 常用住宅开间/进深尺寸

| 空间类型 | 开间（mm） | 进深（mm） |
|----------|-----------|-----------|
| 客厅 | 3600-4500 | 4500-6000 |
| 主卧 | 3300-4200 | 4200-5400 |
| 次卧 | 3000-3600 | 3600-4800 |
| 厨房 | 2400-3000 | 3000-4500 |
| 卫生间 | 1800-2400 | 2400-3600 |
| 走廊 | 1200-1500 | — |
