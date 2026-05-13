# CAD Agent - Trae IDE 集成指南

## 项目概述

本项目将您现有的 CAD Agent 系统（基于 JZXZBOT）迁移到 Trae IDE，实现通过 AI + MCP 协议进行 CAD 语义建模。

## 目录结构

```
CAD_AGENT/
├── .env                          # DeepSeek API 密钥配置
├── appsettings.json              # 主配置文件
├── README.md                     # 本文件
├── Settings/
│   └── Skills/
│       ├── Architect/           # 建筑师技能
│       │   └── SKILL.md
│       └── ResidentialCadGenerator/  # 住宅CAD生成器
│           ├── SKILL.md
│           └── references/       # 参考文档
│               ├── layer-axis.md
│               ├── layer-wall.md
│               └── layer-opening.md
└── MCP Server/
    ├── package.json
    └── mcp_server.py             # MCP 服务器
```

## 快速开始

### 1. 配置 API 密钥

在 `.env` 文件中配置您的 DeepSeek API 密钥：

```
DEEPSEEK_API_KEY=sk-2e5199824ddd44b4835b8717289b7fef
DEEPSEEK_API_URL=https://api.deepseek.com/v1
```

### 2. 启动 MCP 服务器

```bash
cd "D:\TRAE_PROJECT\CAD_AGENT\MCP Server"
python mcp_server.py
```

### 3. 在 Trae IDE 中使用

在 Trae IDE 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "cad-agent": {
      "command": "python",
      "args": ["D:/TRAE_PROJECT/CAD_AGENT/MCP Server/mcp_server.py"],
      "cwd": "D:/TRAE_PROJECT/CAD_AGENT/MCP Server"
    }
  }
}
```

## 可用工具

### 1. execute_cad_csharp_code
在 AutoCAD 中执行 C# 代码生成 CAD 对象

### 2. create_axis_grid
生成建筑轴网
- `horizontal_spacings`: 横向轴线间距数组
- `vertical_spacings`: 纵向轴线间距数组

### 3. create_wall
生成墙体
- `start_x`, `start_y`: 起点坐标
- `end_x`, `end_y`: 终点坐标
- `thickness`: 墙厚（默认240mm）
- `is_external`: 是否为外墙

### 4. create_door
创建门
- `location_x`, `location_y`: 位置坐标
- `width`: 门宽（默认900mm）
- `rotation`: 旋转角度

### 5. create_window
创建窗
- `location_x`, `location_y`: 位置坐标
- `width`: 窗宽（默认1500mm）
- `height`: 窗高（默认1500mm）

## 使用示例

### 生成轴网
```
用户：生成 5×5000 与 6×3000 的轴网
AI：调用 create_axis_grid 工具
参数：{
  "horizontal_spacings": [5000, 5000, 5000, 5000, 5000],
  "vertical_spacings": [3000, 3000, 3000, 3000, 3000, 3000]
}
```

### 绘制墙体
```
用户：在 (0,0) 到 (5000,0) 之间绘制外墙
AI：调用 create_wall 工具
参数：{
  "start_x": 0,
  "start_y": 0,
  "end_x": 5000,
  "end_y": 0,
  "thickness": 240,
  "is_external": true
}
```

## 中国建筑 CAD 标准

本系统遵循以下中国建筑标准：

- **GB/T 50001-2017** 房屋建筑制图统一标准
- **GB 50011-2010** 建筑抗震设计规范
- **图层标准**：A-AXIS（轴网）、A-WALL（墙体）、A-DOOR（门）、A-WIND（窗）、A-DIMS（标注）

## 注意事项

1. **AutoCAD 必须运行**：MCP 服务器需要 AutoCAD 在后台运行
2. **管理员权限**：某些操作可能需要管理员权限
3. **COM 接口**：首次使用可能需要以管理员身份注册 COM 组件

## 故障排除

### 无法连接 AutoCAD
1. 确保 AutoCAD 已启动
2. 检查是否有权限访问 COM 接口
3. 尝试以管理员身份运行

### MCP 请求超时
1. 检查网络连接
2. 确保 MCP 服务器正在运行
3. 查看服务器日志

## 技术支持

如有问题，请检查：
- MCP 服务器日志输出
- AutoCAD COM 接口状态
- DeepSeek API 配额