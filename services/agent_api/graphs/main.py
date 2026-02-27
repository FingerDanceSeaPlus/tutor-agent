from langgraph.graph import StateGraph, END
from typing import Dict, Any
from schemas.state import CoachState
from schemas.stage import Stage
from graphs.base import BaseGraph
from graphs.subgraphs.problem_extraction import ProblemExtractionSubGraph
from graphs.subgraphs.thinking import ThinkingSubGraph
from graphs.subgraphs.coding import CodingSubGraph
from graphs.subgraphs.testing import TestingSubGraph
from graphs.subgraphs.reflecting import ReflectingSubGraph


class TutorAgentGraph(BaseGraph):
    """导师代理图"""
    def __init__(self):
        super().__init__()
        self._add_subgraphs()

    def _add_subgraphs(self):
        """添加子图"""
        # 创建子图实例
        self.problem_extraction_subgraph = ProblemExtractionSubGraph()
        self.thinking_subgraph = ThinkingSubGraph()
        self.coding_subgraph = CodingSubGraph()
        self.testing_subgraph = TestingSubGraph()
        self.reflecting_subgraph = ReflectingSubGraph()

        # 构建子图
        self.problem_extraction_graph = self.problem_extraction_subgraph.build()
        self.thinking_graph = self.thinking_subgraph.build()
        self.coding_graph = self.coding_subgraph.build()
        self.testing_graph = self.testing_subgraph.build()
        self.reflecting_graph = self.reflecting_subgraph.build()

        # 添加子图作为节点
        self.graph.add_node("S1_PROBLEM_graph", self.problem_extraction_graph)
        self.graph.add_node("S2_IDEA_graph", self.thinking_graph)
        self.graph.add_node("S3_CODE_graph", self.coding_graph)
        self.graph.add_node("S4_TEST_graph", self.testing_graph)
        self.graph.add_node("S5_REVIEW_graph", self.reflecting_graph)

        # 添加子图到render_response的边
        self.graph.add_edge("S1_PROBLEM_graph", "render_response")
        self.graph.add_edge("S2_IDEA_graph", "render_response")
        self.graph.add_edge("S3_CODE_graph", "render_response")
        self.graph.add_edge("S4_TEST_graph", "render_response")
        self.graph.add_edge("S5_REVIEW_graph", "render_response")

    async def stage_router(self, state: CoachState) -> str:
        """阶段路由"""
        # 根据当前阶段决定下一个子图
        return f"{state.stage.value}_graph"

    async def render_response(self, state: CoachState) -> Dict[str, Any]:
        """渲染响应"""
        # 根据当前阶段生成不同的响应内容和UI按钮
        buttons = []
        content = ""

        if state.stage == Stage.S1_PROBLEM:
            content = "请提交题目，包括标题、描述、示例和约束条件。"
            buttons = [
                {"label": "确认题面无误", "action": "NEXT"},
                {"label": "补充约束", "action": "EDIT_CONSTRAINTS"},
                {"label": "纠正示例解释", "action": "EDIT_EXAMPLES"}
            ]
        elif state.stage == Stage.S2_IDEA:
            content = "请提交你的解题思路。"
            buttons = [
                {"label": "提示等级：低", "action": "SET_HINT_LEVEL", "payload": {"level": "low"}},
                {"label": "提示等级：中", "action": "SET_HINT_LEVEL", "payload": {"level": "mid"}},
                {"label": "提示等级：高", "action": "SET_HINT_LEVEL", "payload": {"level": "high"}},
                {"label": "给我一个反例", "action": "REQUEST_COUNTEREXAMPLE"},
                {"label": "进入写代码", "action": "NEXT"}
            ]
        elif state.stage == Stage.S3_CODE:
            content = "请提交你的代码。"
            buttons = [
                {"label": "运行示例", "action": "RUN_EXAMPLES"},
                {"label": "格式化代码", "action": "FORMAT_CODE"},
                {"label": "进入测试", "action": "NEXT"},
                {"label": "退回思路", "action": "BACK"}
            ]
        elif state.stage == Stage.S4_TEST:
            content = "请运行测试。"
            buttons = [
                {"label": "提交测试", "action": "RUN_TESTS"},
                {"label": "只跑边界用例", "action": "RUN_EDGE_TESTS"},
                {"label": "回到改代码", "action": "BACK"}
            ]
        elif state.stage == Stage.S5_REVIEW:
            content = "总结与复结。"
            buttons = [
                {"label": "导出复盘", "action": "EXPORT_REPORT"},
                {"label": "下一题（同主题）", "action": "NEXT_PROBLEM"}
            ]

        return {
            "phase_status": f"当前阶段：{state.stage.value}",
            "user_input": state.user_input,
            "transition_reason": state.transition_reason,
            "response": {
                "content": content,
                "buttons": buttons
            }
        }

    async def persist_trace(self, state: CoachState) -> Dict[str, Any]:
        """持久化trace"""
        # 将trace写入存储
        # 暂时简化处理，实际实现需要将trace写入文件或数据库
        print(f"Persisting trace for session {state.session_id}")
        return {}
