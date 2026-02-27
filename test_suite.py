# test_suite.py
"""
测试套件
包含单元测试和集成测试
"""

import unittest
import importlib

# 强制重新加载模块，避免缓存问题
import coach.schemas
import coach.services
import coach.handlers
import coach.graphs.subgraphs.problem_extraction

importlib.reload(coach.schemas)
importlib.reload(coach.services)
importlib.reload(coach.handlers)
importlib.reload(coach.graphs.subgraphs.problem_extraction)

from coach.schemas import CoachState, Problem
from coach.services import StateService, GraphService, LLMService
from coach.handlers import ActionHandler, PhaseHandler
from coach.graphs.subgraphs.problem_extraction import ProblemExtractionSubGraph

class TestStateService(unittest.TestCase):
    """
    测试状态服务
    """
    
    def setUp(self):
        # 重新初始化StateService，确保使用重新加载后的CoachState类
        importlib.reload(coach.services)
        from coach.services import StateService
        self.state_service = StateService()
    
    def test_init_state(self):
        """
        测试初始化状态
        """
        state = self.state_service.init_state()
        self.assertIsInstance(state, CoachState)
        self.assertEqual(state.phase, "need_problem")
        self.assertEqual(state.phase_status, "idle")
    
    def test_has_problem(self):
        """
        测试是否有题目
        """
        state = self.state_service.init_state()
        self.assertFalse(self.state_service.has_problem(state))
        
        # 设置题目
        state.problem = Problem(statement="Test problem")
        state.problem.raw_text = "Test problem text"
        self.assertTrue(self.state_service.has_problem(state))
    
    def test_has_thoughts(self):
        """
        测试是否有思路
        """
        state = self.state_service.init_state()
        self.assertFalse(self.state_service.has_thoughts(state))
        
        # 设置思路
        state.user_attempt.thoughts = "Test thoughts"
        self.assertTrue(self.state_service.has_thoughts(state))
    
    def test_has_code(self):
        """
        测试是否有代码
        """
        state = self.state_service.init_state()
        self.assertFalse(self.state_service.has_code(state))
        
        # 设置代码
        state.user_attempt.code = "Test code"
        self.assertTrue(self.state_service.has_code(state))

class TestLLMService(unittest.TestCase):
    """
    测试LLM服务
    """
    
    def setUp(self):
        self.llm_service = LLMService()
    
    def test_generate_cache_key(self):
        """
        测试生成缓存键
        """
        system_prompt = "Test system prompt"
        user_input = "Test user input"
        cache_key1 = self.llm_service.generate_cache_key(system_prompt, user_input)
        cache_key2 = self.llm_service.generate_cache_key(system_prompt, user_input)
        self.assertEqual(cache_key1, cache_key2)
        
        # 不同输入应该生成不同的缓存键
        different_input = "Different user input"
        cache_key3 = self.llm_service.generate_cache_key(system_prompt, different_input)
        self.assertNotEqual(cache_key1, cache_key3)

class TestProblemExtractionSubGraph(unittest.TestCase):
    """
    测试题目提取子图
    """
    
    def setUp(self):
        self.subgraph = ProblemExtractionSubGraph()
        self.state = StateService().init_state()
        self.state.problem = Problem(statement="")
        self.state.problem.raw_text = "题目：两数之和\n给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那两个整数，并返回它们的数组下标。\n你可以假设每种输入只会对应一个答案。但是，数组中同一个元素不能使用两遍。\n示例：\n输入：nums = [2, 7, 11, 15], target = 9\n输出：[0, 1]\n解释：因为 nums[0] + nums[1] = 2 + 7 = 9，所以返回 [0, 1]。\n约束条件：\n- 2 <= nums.length <= 10^4\n- -10^9 <= nums[i] <= 10^9\n- -10^9 <= target <= 10^9\n- 只会存在一个有效答案"
    
    def test_extract_fields(self):
        """
        测试提取题目字段
        """
        result = self.subgraph.extract_fields(self.state)
        self.assertIsInstance(result, dict)
        self.assertIn("problem", result)
        self.assertIn("analysis", result)

class TestActionHandler(unittest.TestCase):
    """
    测试动作处理器
    """
    
    def setUp(self):
        # 重新初始化ActionHandler和StateService，确保使用重新加载后的模块
        importlib.reload(coach.services)
        importlib.reload(coach.handlers)
        from coach.services import StateService
        from coach.handlers import ActionHandler
        self.action_handler = ActionHandler()
        self.state = StateService().init_state()
        self.state.problem = Problem(statement="Test problem")
        self.state.problem.raw_text = "Test problem text"
    
    async def test_route_action(self):
        """
        测试路由动作
        """
        # 测试处理设置题目动作
        from chainlit import Action
        action = Action(name="set_problem", value="set_problem", label="设置题目", payload={})
        result = await self.action_handler.route_action(self.state, action)
        self.assertIsInstance(result, CoachState)

class TestPhaseHandler(unittest.TestCase):
    """
    测试阶段处理器
    """
    
    def setUp(self):
        # 重新初始化PhaseHandler和StateService，确保使用重新加载后的模块
        importlib.reload(coach.services)
        importlib.reload(coach.handlers)
        from coach.services import StateService
        from coach.handlers import PhaseHandler
        self.state = StateService().init_state()
        self.state.problem = Problem(statement="Test problem")
        self.state.problem.raw_text = "Test problem text"
        self.phase_handler = PhaseHandler(self.state)
    
    def test_validate_state(self):
        """
        测试验证状态
        """
        result = self.phase_handler.validate_state()
        self.assertTrue(result)
    
    def test_update_state(self):
        """
        测试更新状态
        """
        updates = {"phase": "thinking"}
        result = self.phase_handler.update_state(updates)
        self.assertIsInstance(result, CoachState)
        self.assertEqual(result.phase, "thinking")

if __name__ == "__main__":
    import asyncio
    
    # 运行异步测试
    async def run_tests():
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestStateService)
        await asyncio.gather(*(test_case() for test_case in test_suite))
        
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestLLMService)
        await asyncio.gather(*(test_case() for test_case in test_suite))
        
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestProblemExtractionSubGraph)
        await asyncio.gather(*(test_case() for test_case in test_suite))
        
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestActionHandler)
        await asyncio.gather(*(test_case() for test_case in test_suite))
        
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestPhaseHandler)
        await asyncio.gather(*(test_case() for test_case in test_suite))
    
    # 运行同步测试
    unittest.main()
