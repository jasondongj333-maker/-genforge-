"""
通过 MCP 执行萨伏伊别墅绘图
"""

import json
import subprocess
import sys

def send_mcp_request(method, params=None):
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    process = subprocess.Popen(
        ["python", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=r"D:\TRAE_PROJECT\CAD_AGENT\MCP Server"
    )

    stdout, stderr = process.communicate(input=json.dumps(request) + "\n", timeout=10)
    return stdout, stderr

def main():
    print("=== 通过 MCP 执行萨伏伊别墅绘图 ===\n")

    # 读取 C# 代码
    with open(r"D:\TRAE_PROJECT\CAD_AGENT\VillaSavoyePlan.cs", "r", encoding="utf-8") as f:
        csharp_code = f.read()

    print("1. 检查 AutoCAD 连接状态...")
    stdout, stderr = send_mcp_request("tools/call", {
        "name": "get_autocad_status",
        "arguments": {}
    })
    print(stdout)

    print("\n2. 准备执行萨伏伊别墅绘图代码...")
    print(f"   代码长度: {len(csharp_code)} 字符")

    print("\n3. 发送绘图请求...")
    stdout, stderr = send_mcp_request("tools/call", {
        "name": "execute_cad_csharp_code",
        "arguments": {
            "csharp_code": csharp_code
        }
    })
    print(stdout)

if __name__ == "__main__":
    main()
