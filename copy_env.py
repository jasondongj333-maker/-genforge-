"""
复制 .env 文件到 dist 目录
"""
import shutil
import os

src = ".env"
dst = "dist/.env"

if os.path.exists(src):
    if os.path.exists(dst):
        os.remove(dst)
        print(f"已删除旧文件: {dst}")
    shutil.copy(src, dst)
    print(f"✅ 已复制 {src} -> {dst}")
    
    # 验证
    if os.path.exists(dst):
        print(f"✅ 目标文件存在: {dst}")
        with open(dst, 'r', encoding='utf-8') as f:
            print("\n文件内容预览:")
            print(f.read())
    else:
        print("❌ 复制失败！")
else:
    print(f"❌ 源文件不存在: {src}")
