# CAD Agent 快速使用指南

## ✅ 项目已创建完成

您的 CAD Agent 项目已成功迁移到 Trae IDE！

## 📁 项目位置

```
D:\TRAE_PROJECT\CAD_AGENT\
├── .env                          # DeepSeek API 密钥
├── appsettings.json              # 主配置
├── mcp_config.json               # MCP 服务器配置
├── README.md                     # 详细文档
├── QUICKSTART.md                 # 本文件
├── Settings/
│   └── Skills/
│       ├── Architect/            # 建筑师技能
│       └── ResidentialCadGenerator/  # 住宅CAD生成器
└── MCP Server/
    └── mcp_server.py             # MCP 服务器（已运行）
```

## 🚀 快速开始

### 1. MCP 服务器状态

MCP 服务器已启动并在**模拟模式**下运行（等待 AutoCAD 连接）。

### 2. 配置 Trae IDE MCP

在 Trae IDE 设置中添加以下 MCP 配置：

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

### 3. 启动 AutoCAD

为了获得完整的 CAD 功能，请：

1. 启动 AutoCAD 2023 或更高版本
2. 加载 `CadAgentServer.dll` 插件（在 AutoCAD 中使用 `NETLOAD` 命令）
3. MCP 服务器将自动连接到 AutoCAD

## 🎯 使用示例

### 生成轴网
```
用户：生成 5×5000 与 6×3000 的轴网
AI：调用 create_axis_grid 工具
```

### 绘制墙体
```
用户：在 (0,0) 到 (5000,0) 之间绘制外墙
AI：调用 create_wall 工具
```

### 创建门窗
```
用户：在位置 (1000,0) 创建宽900mm的门
AI：调用 create_door 工具
```

## 📋 可用 Skills

### 1. Architect（建筑师）
专注于建筑空间设计、功能分区、规范合规

### 2. ResidentialCadGenerator（住宅CAD生成器）
生成符合中国建筑标准的住宅平面图（轴网+墙体+门窗）

## � 可用工具

| 工具名 | 功能 | 主要参数 |
|--------|------|---------|
| `create_axis_grid` | 生成轴网 | horizontal_spacings, vertical_spacings |
| `create_wall` | 绘制墙体 | start_x/y, end_x/y, thickness |
| `create_door` | 创建门 | location_x/y, width, rotation |
| `create_window` | 创建窗 | location_x/y, width, height |
| `execute_cad_csharp_code` | 执行C#代码 | csharp_code |
| `get_autocad_status` | 获取状态 | - |

## ⚠️ 注意事项

1. **模拟模式**：当前 MCP 服务器在模拟模式下运行，等待 AutoCAD 连接
2. **AutoCAD 要求**：需要 AutoCAD 2023+ 并加载 CadAgentServer.dll
3. **API 配额**：DeepSeek API 有使用限制，注意配额消耗

## 📞 下一步

1. 在 Trae IDE 中配置 MCP 连接
2. 启动 AutoCAD 并加载插件
3. 开始使用自然语言生成 CAD 图纸！

## ❓ 故障排除

**MCP 服务器无法启动？**
```bash
cd D:\TRAE_PROJECT\CAD_AGENT\MCP Server
python mcp_server.py
```

**无法连接 AutoCAD？**
- 确保 AutoCAD 已启动
- 检查是否以管理员权限运行
- 确认 CadAgentServer.dll 已加载

**API 调用失败？**
- 检查 .env 文件中的 API 密钥
- 确认 DeepSeek API 配额充足