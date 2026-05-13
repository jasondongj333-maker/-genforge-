"""
金锤子 (GenForge) - 主程序
CAD 语义建模智能体
"""
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from Core.agent import GenForgeAgent
from UI.desktop_app import GenForgeApp


def main():
    """主函数"""
    print("==================================================")
    print("🔨 金锤子 GenForge 正在启动...")
    print("==================================================")
    
    # 初始化 Agent
    agent = GenForgeAgent()
    
    # 启动界面
    app = GenForgeApp(agent)
    app.run()


if __name__ == "__main__":
    main()
