#!/usr/bin/env python
"""简单版测试"""

import sys
import os
from pathlib import Path

print("=== 模拟打包后环境 ===")

# 模拟 PyInstaller 环境
sys.frozen = True
sys._MEIPASS = "D:\\ai_cad_agent_001\\publish\\build\\GenForge"
sys.executable = "D:\\ai_cad_agent_001\\publish\\dist\\GenForge.exe"

config = {}
possible_paths = []

# 测试 _load_env 逻辑
if hasattr(sys, '_MEIPASS'):
    exe_dir = Path(sys.executable).parent
    possible_paths.append(exe_dir / ".env")
    possible_paths.append(Path(sys._MEIPASS) / ".env")

src_dir = Path(__file__).parent
possible_paths.append(src_dir / ".env")
possible_paths.append(Path.cwd() / ".env")

print("\nPossible paths:")
for idx, p in enumerate(possible_paths, 1):
    exists = p.exists()
    print(f"  [{idx}] {p} -> {'EXISTS' if exists else 'NOT EXISTS'}")
    
    if exists:
        print("    Loading this file")
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

print(f"\nConfig loaded: {config}")
