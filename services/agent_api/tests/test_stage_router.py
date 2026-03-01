import asyncio
import json
from services.agent_api.graphs.main import TutorAgentGraph
from services.agent_api.schemas.state import CoachState
from services.agent_api.schemas.stage import Stage

async def test_problem_stage_input():
    """测试题目阶段输入"""
    print("测试题目阶段输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input="给定一个数组，找出其中两个数的和等于目标值。例如，输入[2, 7, 11, 15]，目标值9，返回[0, 1]"
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"题目阶段输入结果: {result}")
    
    # 检查是否返回了next_stage
    if "next_stage" in result:
        print("✓ 题目阶段输入测试通过")
    else:
        print("✗ 题目阶段输入测试失败")

async def test_idea_stage_input():
    """测试思路阶段输入"""
    print("测试思路阶段输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S2_IDEA,
        user_input="我可以使用哈希表来解决这个问题。遍历数组，对于每个元素，检查目标值减去当前元素的结果是否在哈希表中。如果存在，返回两个索引；如果不存在，将当前元素加入哈希表。"
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"思路阶段输入结果: {result}")
    
    # 检查是否返回了next_stage
    if "next_stage" in result:
        print("✓ 思路阶段输入测试通过")
    else:
        print("✗ 思路阶段输入测试失败")

async def test_code_stage_input():
    """测试编码阶段输入"""
    print("测试编码阶段输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S3_CODE,
        user_input="def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []"
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"编码阶段输入结果: {result}")
    
    # 检查是否返回了next_stage
    if "next_stage" in result:
        print("✓ 编码阶段输入测试通过")
    else:
        print("✗ 编码阶段输入测试失败")

async def test_test_stage_input():
    """测试测试阶段输入"""
    print("测试测试阶段输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S4_TEST,
        user_input="测试结果显示，当输入[2, 7, 11, 15]和目标值9时，返回[0, 1]，测试通过。但当输入[3, 2, 4]和目标值6时，返回[]，测试失败。"
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"测试阶段输入结果: {result}")
    
    # 检查是否返回了next_stage
    if "next_stage" in result:
        print("✓ 测试阶段输入测试通过")
    else:
        print("✗ 测试阶段输入测试失败")

async def test_review_stage_input():
    """测试复盘阶段输入"""
    print("测试复盘阶段输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S5_REVIEW,
        user_input="这个问题的核心是使用哈希表来降低时间复杂度。通过一次遍历，我们可以在O(n)的时间复杂度内解决问题。关键是要理解哈希表的查找时间复杂度是O(1)，这使得整个算法效率很高。"
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"复盘阶段输入结果: {result}")
    
    # 检查是否返回了next_stage
    if "next_stage" in result:
        print("✓ 复盘阶段输入测试通过")
    else:
        print("✗ 复盘阶段输入测试失败")

async def test_low_confidence_input():
    """测试低置信度输入"""
    print("测试低置信度输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input="今天天气真好，适合出去散步。"
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"低置信度输入结果: {result}")
    
    # 检查是否返回了错误信息
    if "error" in result:
        print("✓ 低置信度输入测试通过")
    else:
        print("✗ 低置信度输入测试失败")

async def test_empty_input():
    """测试空输入"""
    print("测试空输入...")
    
    # 创建TutorAgentGraph实例
    graph = TutorAgentGraph()
    
    # 创建初始状态
    state = CoachState(
        stage=Stage.S1_PROBLEM,
        user_input=""
    )
    
    # 调用stage_router函数
    result = await graph.stage_router(state)
    
    # 验证结果
    print(f"空输入结果: {result}")
    
    # 检查是否返回了空字典
    if result == {}:
        print("✓ 空输入测试通过")
    else:
        print("✗ 空输入测试失败")

async def run_all_tests():
    """运行所有测试"""
    print("开始测试stage_router智能路由功能...")
    
    await test_problem_stage_input()
    await test_idea_stage_input()
    await test_code_stage_input()
    await test_test_stage_input()
    await test_review_stage_input()
    await test_low_confidence_input()
    await test_empty_input()
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
