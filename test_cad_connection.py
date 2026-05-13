#!/usr/bin/env python
"""AutoCAD COM 连接诊断工具"""

import win32com.client
import pythoncom
import sys
import time


def test_connection():
    print("=== AutoCAD COM 连接诊断 ===")
    print(f"Python 版本: {sys.version}")
    print(f"系统位数: {64 if sys.maxsize > 2 ** 32 else 32}位")

    # 尝试不同的 ProgID
    prog_ids = [
        "AutoCAD.Application",
        "AutoCAD.Application.24",  # AutoCAD 2024
        "AutoCAD.Application.25",  # AutoCAD 2025
        "AutoCAD.Application.23",  # AutoCAD 2023
    ]

    print("\n尝试连接已运行的 AutoCAD...")
    for prog_id in prog_ids:
        try:
            pythoncom.CoInitialize()
            acad = win32com.client.GetActiveObject(prog_id)
            ver = getattr(acad, "Version", "未知")
            print(f"✓ 使用 ProgID '{prog_id}' 连接成功!")
            print(f"  AutoCAD 版本: {ver}")
            print(f"  是否可见: {acad.Visible}")
            return True
        except Exception as e:
            print(f"✗ ProgID '{prog_id}' 失败: {str(e)[:80]}")

    print("\n尝试启动新的 AutoCAD 实例...")
    for prog_id in prog_ids:
        try:
            acad = win32com.client.Dispatch(prog_id)
            acad.Visible = True
            time.sleep(2)
            ver = getattr(acad, "Version", "未知")
            print(f"✓ 使用 ProgID '{prog_id}' 启动成功!")
            print(f"  AutoCAD 版本: {ver}")
            return True
        except Exception as e:
            print(f"✗ ProgID '{prog_id}' 失败: {str(e)[:80]}")

    print("\n❌ 所有尝试都失败了!")
    print("请检查:")
    print("1. AutoCAD 是否已正确安装")
    print("2. 是否以相同权限运行 (管理员/普通用户)")
    print("3. AutoCAD COM 接口是否正常注册")
    return False


if __name__ == "__main__":
    test_connection()