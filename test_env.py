import sys
import os
from pathlib import Path

print("=== 测试环境配置加载 ===")
print(f"sys.executable: {sys.executable}")
print(f"sys.frozen: {getattr(sys, 'frozen', 'Not frozen')}")
print(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}")

# 模拟 _load_env 的逻辑
possible_paths = []

if hasattr(sys, '_MEIPASS'):
    exe_dir = Path(sys.executable).parent
    possible_paths.append(exe_dir / ".env")
    possible_paths.append(Path(sys._MEIPASS) / ".env")

src_dir = Path(__file__).parent
possible_paths.append(src_dir / ".env")

possible_paths.append(Path.cwd() / ".env")

print("\n尝试路径:")
for p in possible_paths:
    exists = p.exists()
    print(f"  {p} -> {'✓ 存在' if exists else '✗ 不存在'}")
    if exists:
        print(f"    内容:")
        try:
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        print(f"      {line}")
        except Exception as e:
            print(f"      读取错误: {e}")
