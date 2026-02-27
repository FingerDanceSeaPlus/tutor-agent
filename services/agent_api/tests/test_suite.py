import asyncio
import pytest
from schemas.stage import Stage
from schemas.state import CoachState, ProblemSpec, IdeaSpec, CodeSpec, RunReport, TestReport
from graphs.subgraphs.problem_extraction import ProblemExtractionSubGraph
from graphs.subgraphs.thinking import ThinkingSubGraph
from graphs.subgraphs.coding import CodingSubGraph
from graphs.subgraphs.testing import TestingSubGraph
from graphs.subgraphs.reflecting import ReflectingSubGraph
from services.llm_service import LLMService
from services.runner_service import RunnerService
from services.trace_service import TraceService
from services.graph_service import GraphService


class TestStageEnum:
    """测试Stage枚举"""
    def test_stage_next(self):
        """测试获取下一个阶段"""
        assert Stage.S1_PROBLEM.next() == Stage.S2_IDEA
        assert Stage.S2_IDEA.next() == Stage.S3_CODE
        assert Stage.S3_CODE.next() == Stage.S4_TEST
        assert Stage.S4_TEST.next() == Stage.S5_REVIEW
        assert Stage.S5_REVIEW.next() == Stage.S5_REVIEW

    def test_stage_prev(self):
        """测试获取上一个阶段"""
        assert Stage.S1_PROBLEM.prev() == Stage.S1_PROBLEM
        assert Stage.S2_IDEA.prev() == Stage.S1_PROBLEM
        assert Stage.S3_CODE.prev() == Stage.S2_IDEA
        assert Stage.S4_TEST.prev() == Stage.S3_CODE
        assert Stage.S5_REVIEW.prev() == Stage.S4_TEST


class TestStateSchema:
    """测试State Schema"""
    def test_coach_state_initialization(self):
        """测试CoachState初始化"""
        state = CoachState()
        assert state.stage == Stage.S1_PROBLEM
        assert state.hint_level == "mid"
        assert state.problem is None
        assert state.idea is None
        assert state.code is None
        assert state.run_report is None
        assert state.test_report is None
        assert state.history == []
        assert state.trace.stages == {}
        assert state.trace.events == []

    def test_problem_spec(self):
        """测试ProblemSpec"""
        problem = ProblemSpec(
            title="测试题目",
            description="测试描述",
            examples=[{"input": "1", "output": "2"}],
            constraints=["约束1", "约束2"]
        )
        assert problem.title == "测试题目"
        assert problem.description == "测试描述"
        assert len(problem.examples) == 1
        assert len(problem.constraints) == 2
        assert problem.ready == False


class TestSubGraphs:
    """测试子图"""
    @pytest.mark.asyncio
    async def test_problem_extraction_subgraph(self):
        """测试题目提取子图"""
        subgraph = ProblemExtractionSubGraph()
        graph = subgraph.build()
        
        # 创建测试状态
        state = CoachState(
            user_input="题目：两数之和\n描述：给定一个整数数组和一个目标值，找出和为目标值的两个数的索引。\n示例：输入：[2,7,11,15], 目标：9，输出：[0,1]\n约束：数组长度至少为2"
        )
        
        # 编译图并运行
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(state.model_dump())
        assert "problem" in result
        assert result["problem"].title == "提取的标题"

    @pytest.mark.asyncio
    async def test_thinking_subgraph(self):
        """测试思路分析子图"""
        subgraph = ThinkingSubGraph()
        graph = subgraph.build()
        
        # 创建测试状态
        state = CoachState(
            user_input="使用哈希表存储已遍历的元素，遍历数组时查找目标值减去当前元素的差是否在哈希表中"
        )
        
        # 编译图并运行
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(state.model_dump())
        assert "idea" in result
        assert result["idea"].user_idea_raw == "使用哈希表存储已遍历的元素，遍历数组时查找目标值减去当前元素的差是否在哈希表中"

    @pytest.mark.asyncio
    async def test_coding_subgraph(self):
        """测试编码子图"""
        subgraph = CodingSubGraph()
        graph = subgraph.build()
        
        # 创建测试状态
        state = CoachState(
            user_input="def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []"
        )
        
        # 编译图并运行
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(state.model_dump())
        assert "code" in result
        assert result["code"].language == "python"

    @pytest.mark.asyncio
    async def test_testing_subgraph(self):
        """测试测试子图"""
        subgraph = TestingSubGraph()
        graph = subgraph.build()
        
        # 创建测试状态
        state = CoachState(
            code=CodeSpec(
                language="python",
                code_text="def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []",
                format_ok=True,
                entrypoint_detected=True
            )
        )
        
        # 编译图并运行
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(state.model_dump())
        assert "test_report" in result

    @pytest.mark.asyncio
    async def test_reflecting_subgraph(self):
        """测试复盘子图"""
        subgraph = ReflectingSubGraph()
        graph = subgraph.build()
        
        # 创建测试状态
        state = CoachState(
            problem=ProblemSpec(
                title="两数之和",
                description="给定一个整数数组和一个目标值，找出和为目标值的两个数的索引。",
                examples=[{"input": "[2,7,11,15], 9", "output": "[0,1]"}],
                constraints=["数组长度至少为2"],
                ready=True
            ),
            idea=IdeaSpec(
                user_idea_raw="使用哈希表存储已遍历的元素，遍历数组时查找目标值减去当前元素的差是否在哈希表中",
                analysis="思路正确，使用哈希表可以将时间复杂度从O(n²)降低到O(n)",
                guidance="可以进一步优化代码结构，添加边界条件检查"
            ),
            code=CodeSpec(
                language="python",
                code_text="def two_sum(nums, target):\n    hash_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in hash_map:\n            return [hash_map[complement], i]\n        hash_map[num] = i\n    return []",
                format_ok=True,
                entrypoint_detected=True
            ),
            test_report=TestReport(
                passed=True,
                results=[],
                total_time=0.1,
                memory_usage=10.0
            )
        )
        
        # 编译图并运行
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(state.model_dump())
        assert "transition_reason" in result
        assert result["transition_reason"] == "生成了完整的复盘报告"


class TestServices:
    """测试服务"""
    @pytest.mark.asyncio
    async def test_llm_service(self):
        """测试LLM服务"""
        service = LLMService()
        response = await service.generate("测试提示词")
        assert isinstance(response, str)
        assert "LLM响应" in response

    @pytest.mark.asyncio
    async def test_runner_service(self):
        """测试Runner服务"""
        service = RunnerService()
        code = "print('Hello, World!')"
        result = await service.run_code(code, "python")
        assert "ok" in result
        assert result["ok"] == True

    def test_trace_service(self):
        """测试Trace服务"""
        service = TraceService(storage_type="jsonl")
        session_id = "test_session"
        trace = {
            "events": [{
                "ts": "2024-01-01T00:00:00",
                "stage": "S1_PROBLEM",
                "kind": "USER_INPUT",
                "payload": {"content": "测试输入"}
            }],
            "hint_level": "mid",
            "current_stage": "S1_PROBLEM"
        }
        service.store_trace(session_id, trace)
        retrieved_trace = service.get_trace(session_id)
        assert len(retrieved_trace["events"]) > 0

    def test_graph_service(self):
        """测试Graph服务"""
        service = GraphService()
        state = CoachState()
        updated_state = service.update_state(state, {"hint_level": "high"})
        assert updated_state.hint_level == "high"
        assert service.validate_state(state) == False


if __name__ == "__main__":
    pytest.main([__file__])
