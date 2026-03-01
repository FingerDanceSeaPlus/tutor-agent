import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from services.agent_api.graphs.base import BaseGraph
from services.agent_api.schemas.state import CoachState
from services.agent_api.schemas.stage import Stage

async def test_text_input():
    """测试文本输入处理"""
    print("测试文本输入...")
    
    # 创建BaseGraph实例
    graph = BaseGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input="这是一个测试问题"
    )
    
    # 调用ingest_user_input函数
    result = await graph.ingest_user_input(state)
    
    # 验证结果
    assert "history" in result, "历史记录应该被更新"
    assert len(result["history"]) == 1, "应该添加一条历史记录"
    assert result["history"][0].role == "user", "消息角色应该是user"
    assert result["history"][0].content == "这是一个测试问题", "消息内容应该正确"
    
    assert "trace" in result, "追踪信息应该被更新"
    assert len(result["trace"]["events"]) == 1, "应该添加一个追踪事件"
    assert result["trace"]["events"][0].kind == "USER_INPUT", "事件类型应该是USER_INPUT"
    assert result["trace"]["events"][0].payload["input_type"] == "TEXT", "输入类型应该是TEXT"
    
    print("✓ 文本输入测试通过")

async def test_action_input():
    """测试动作输入处理"""
    print("测试动作输入...")
    
    # 创建BaseGraph实例
    graph = BaseGraph()
    
    # 创建动作输入
    action_input = json.dumps({
        "type": "ACTION",
        "payload": {
            "action": "NEXT"
        }
    })
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input=action_input
    )
    
    # 调用ingest_user_input函数
    result = await graph.ingest_user_input(state)
    
    # 验证结果
    assert "history" in result, "历史记录应该被更新"
    assert len(result["history"]) == 1, "应该添加一条历史记录"
    assert result["history"][0].role == "user", "消息角色应该是user"
    assert "Action: NEXT" in result["history"][0].content, "消息内容应该包含动作信息"
    
    assert "trace" in result, "追踪信息应该被更新"
    assert len(result["trace"]["events"]) == 1, "应该添加一个追踪事件"
    assert result["trace"]["events"][0].kind == "USER_INPUT", "事件类型应该是USER_INPUT"
    assert result["trace"]["events"][0].payload["input_type"] == "ACTION", "输入类型应该是ACTION"
    assert result["trace"]["events"][0].payload["action"] == "NEXT", "动作应该是NEXT"
    
    print("✓ 动作输入测试通过")

async def test_file_input():
    """测试文件输入处理"""
    print("测试文件输入...")
    
    # 创建BaseGraph实例
    graph = BaseGraph()
    
    # 创建文件输入
    file_input = json.dumps({
        "type": "FILE",
        "payload": {
            "file_name": "test.py",
            "content": "print('Hello, World!')"
        }
    })
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input=file_input
    )
    
    # 调用ingest_user_input函数
    result = await graph.ingest_user_input(state)
    
    # 验证结果
    assert "history" in result, "历史记录应该被更新"
    assert len(result["history"]) == 1, "应该添加一条历史记录"
    assert result["history"][0].role == "user", "消息角色应该是user"
    assert "File uploaded: test.py" in result["history"][0].content, "消息内容应该包含文件信息"
    
    assert "trace" in result, "追踪信息应该被更新"
    assert len(result["trace"]["events"]) == 1, "应该添加一个追踪事件"
    assert result["trace"]["events"][0].kind == "USER_INPUT", "事件类型应该是USER_INPUT"
    assert result["trace"]["events"][0].payload["input_type"] == "FILE", "输入类型应该是FILE"
    assert result["trace"]["events"][0].payload["file_name"] == "test.py", "文件名应该正确"
    
    print("✓ 文件输入测试通过")

async def test_empty_input():
    """测试空输入处理"""
    print("测试空输入...")
    
    # 创建BaseGraph实例
    graph = BaseGraph()
    
    # 创建初始状态（无用户输入）
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input=None
    )
    
    # 调用ingest_user_input函数
    result = await graph.ingest_user_input(state)
    
    # 验证结果
    assert result == {}, "空输入应该返回空字典"
    
    print("✓ 空输入测试通过")

async def run_all_tests():
    """运行所有测试"""
    print("开始测试ingest_user_input函数...")
    
    await test_text_input()
    await test_action_input()
    await test_file_input()
    await test_empty_input()
    
    print("\n🎉 所有测试通过！")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
