"""
金锤子 (GenForge) - 阶段二测试脚本
测试 MCP 服务器、技能库
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_imports():
    """测试导入"""
    print("=" * 50)
    print("🔍 测试导入...")
    print("=" * 50)
    
    try:
        from Core.config import LLM_CONFIG
        print("✅ Core.config 导入成功")
    except Exception as e:
        print(f"❌ Core.config 导入失败: {e}")
    
    try:
        from Core.agent import GenForgeAgent
        print("✅ Core.agent 导入成功")
    except Exception as e:
        print(f"❌ Core.agent 导入失败: {e}")
    
    try:
        from Skills.cad_skills import CADSkillLibrary
        print("✅ Skills.cad_skills 导入成功")
    except Exception as e:
        print(f"❌ Skills.cad_skills 导入失败: {e}")
    
    try:
        from Skills.revit_skills import RevitSkillLibrary
        print("✅ Skills.revit_skills 导入成功")
    except Exception as e:
        print(f"❌ Skills.revit_skills 导入失败: {e}")
    
    try:
        from MCP.server import MCPServer
        print("✅ MCP.server 导入成功")
    except Exception as e:
        print(f"❌ MCP.server 导入失败: {e}")
    
    try:
        from MCP.cad_connector import AutoCADConnector
        print("✅ MCP.cad_connector 导入成功")
    except Exception as e:
        print(f"❌ MCP.cad_connector 导入失败: {e}")


def test_cad_skills():
    """测试 CAD 技能"""
    print("\n" + "=" * 50)
    print("🔍 测试 CAD 技能...")
    print("=" * 50)
    
    try:
        from Skills.cad_skills import CADSkillLibrary
        
        library = CADSkillLibrary()
        print(f"✅ 技能库创建成功")
        print(f"📋 可用技能: {library.list_skills()}")
        
        # 测试创建图层技能
        skill = library.get_skill('create_layer')
        if skill:
            result = skill.execute({'layer_name': 'TEST_LAYER', 'color': 1})
            print(f"✅ create_layer 技能执行成功")
            print(f"   状态: {result.get('status')}")
            print(f"   代码长度: {len(result.get('code', ''))} 字符")
        
        # 测试绘制墙体技能
        skill = library.get_skill('draw_wall')
        if skill:
            result = skill.execute({'thickness': 200, 'height': 2800})
            print(f"✅ draw_wall 技能执行成功")
        
        # 测试绘制轴网技能
        skill = library.get_skill('draw_grid')
        if skill:
            result = skill.execute({'rows': 5, 'cols': 4, 'spacing_x': 6000})
            print(f"✅ draw_grid 技能执行成功")
            
    except Exception as e:
        print(f"❌ CAD 技能测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_revit_skills():
    """测试 Revit 技能"""
    print("\n" + "=" * 50)
    print("🔍 测试 Revit 技能...")
    print("=" * 50)
    
    try:
        from Skills.revit_skills import RevitSkillLibrary
        
        library = RevitSkillLibrary()
        print(f"✅ Revit 技能库创建成功")
        print(f"📋 可用技能: {library.list_skills()}")
        
        # 测试创建墙体
        skill = library.get_skill('create_wall')
        if skill:
            result = skill.execute({'width': 6000, 'height': 2800, 'thickness': 200})
            print(f"✅ create_wall 技能执行成功")
        
    except Exception as e:
        print(f"❌ Revit 技能测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_agent():
    """测试 Agent"""
    print("\n" + "=" * 50)
    print("🔍 测试 Agent...")
    print("=" * 50)
    
    try:
        from Core.agent import GenForgeAgent
        
        agent = GenForgeAgent()
        print("✅ Agent 创建成功")
        print(f"📋 当前目标: {agent.current_target}")
        
        # 测试对话（不调用 API）
        print("\n📝 测试对话能力...")
        
        # 检查技能库是否正确
        print(f"✅ CAD 技能: {agent.cad_skills.list_skills()}")
        print(f"✅ Revit 技能: {agent.revit_skills.list_skills()}")
        
    except Exception as e:
        print(f"❌ Agent 测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("\n" + "=" * 60)
    print("🔨 金锤子 GenForge - 阶段二测试")
    print("=" * 60)
    
    test_imports()
    test_cad_skills()
    test_revit_skills()
    test_agent()
    
    print("\n" + "=" * 60)
    print("✅ 阶段二测试完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 运行 python main.py 启动金锤子桌面应用")
    print("2. 在聊天窗口输入建模指令")
    print("3. 观察代码生成效果")


if __name__ == "__main__":
    main()
