from langgraph.graph import StateGraph, END
from typing import Dict, Any
from ..schemas.state import CoachState
from ..schemas.stage import Stage
from .base import BaseGraph
from .subgraphs.problem_extraction import ProblemExtractionSubGraph
from .subgraphs.thinking import ThinkingSubGraph
from .subgraphs.coding import CodingSubGraph
from .subgraphs.testing import TestingSubGraph
from .subgraphs.reflecting import ReflectingSubGraph
from ..services.llm_service import LLMService


class TutorAgentGraph(BaseGraph):
    """导师代理图"""
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()
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
        self.problem_extraction_graph = self.problem_extraction_subgraph.build().compile()
        self.thinking_graph = self.thinking_subgraph.build().compile()
        self.coding_graph = self.coding_subgraph.build().compile()
        self.testing_graph = self.testing_subgraph.build().compile()
        self.reflecting_graph = self.reflecting_subgraph.build().compile()

        # 添加子图作为节点
        self.graph.add_node("S1_PROBLEM_graph", self.problem_extraction_graph)
        self.graph.add_node("S2_IDEA_graph", self.thinking_graph)
        self.graph.add_node("S3_CODE_graph", self.coding_graph)
        self.graph.add_node("S4_TEST_graph", self.testing_graph)
        self.graph.add_node("S5_REVIEW_graph", self.reflecting_graph)

        # 添加子图到render_response的边
        # 添加条件边，将 stage_router 与子图连接
        self.graph.add_conditional_edges(
            "stage_router",
            self._route_to_subgraph,  # 路由函数
            {
                "S1_PROBLEM_graph": "S1_PROBLEM_graph",
                "S2_IDEA_graph": "S2_IDEA_graph",
                "S3_CODE_graph": "S3_CODE_graph",
                "S4_TEST_graph": "S4_TEST_graph",
                "S5_REVIEW_graph": "S5_REVIEW_graph"
            }
        )
        self.graph.add_edge("S1_PROBLEM_graph", "render_response")
        self.graph.add_edge("S2_IDEA_graph", "render_response")
        self.graph.add_edge("S3_CODE_graph", "render_response")
        self.graph.add_edge("S4_TEST_graph", "render_response")
        self.graph.add_edge("S5_REVIEW_graph", "render_response")

    async def stage_router(self, state: CoachState) -> Dict[str, Any]:
        """阶段路由"""
        # 检查是否有用户输入
        if not state.user_input:
            return {}
        
        try:
            # 模拟置信度计算（实际实现中会使用LLM）
            confidence_scores = self._calculate_confidence(state.user_input)
            
            # 设置置信度阈值
            confidence_threshold = 0.8
            
            # 找出置信度最高且超过阈值的阶段
            best_stage = None
            best_confidence = 0.0
            
            for stage, confidence in confidence_scores.items():
                if confidence > best_confidence and confidence >= confidence_threshold:
                    best_confidence = confidence
                    best_stage = stage
            
            # 如果找到合适的阶段，返回路由信息
            if best_stage:
                return {"next_stage": best_stage}
            else:
                # 所有阶段置信度都不达标，返回错误信息
                return {
                    "error": "用户的问题超出能力范围",
                    "message": "无法确定用户输入属于哪个阶段，请提供更明确的信息"
                }
        
        except Exception as e:
            # 处理错误情况
            return {
                "error": "路由失败",
                "message": f"智能路由过程中出现错误: {str(e)}"
            }
    
    def _calculate_confidence(self, user_input: str) -> Dict[str, float]:
        """计算用户输入属于各阶段的置信度"""
        # 模拟置信度计算
        confidence_scores = {
            "S1_PROBLEM": 0.0,
            "S2_IDEA": 0.0,
            "S3_CODE": 0.0,
            "S4_TEST": 0.0,
            "S5_REVIEW": 0.0
        }
        
        # 根据输入内容判断置信度
        user_input_lower = user_input.lower()
        
        # 题目阶段关键词
        problem_keywords = ["题目", "给定", "数组", "目标值", "示例", "约束", "输入", "输出"]
        for keyword in problem_keywords:
            if keyword in user_input_lower:
                confidence_scores["S1_PROBLEM"] += 0.2
        
        # 思路阶段关键词
        idea_keywords = ["思路", "哈希表", "遍历", "算法", "设计", "解决", "方法", "可以使用", "我可以", "解决这个问题", "遍历数组", "检查", "如果存在", "返回", "加入"]
        for keyword in idea_keywords:
            if keyword in user_input_lower:
                confidence_scores["S2_IDEA"] += 0.15
        
        # 编码阶段关键词
        code_keywords = ["def ", "class ", "for ", "if ", "return ", "print(", "import "]
        for keyword in code_keywords:
            if keyword in user_input:
                confidence_scores["S3_CODE"] += 0.2
        
        # 测试阶段关键词
        test_keywords = ["测试", "结果", "失败", "通过", "case", "用例"]
        for keyword in test_keywords:
            if keyword in user_input_lower:
                confidence_scores["S4_TEST"] += 0.2
        
        # 复盘阶段关键词
        review_keywords = ["复盘", "总结", "核心", "时间复杂度", "关键", "效率"]
        for keyword in review_keywords:
            if keyword in user_input_lower:
                confidence_scores["S5_REVIEW"] += 0.2
        
        # 确保置信度不超过1.0
        for stage in confidence_scores:
            confidence_scores[stage] = min(confidence_scores[stage], 1.0)
        
        return confidence_scores

    def _route_to_subgraph(self, state: CoachState) -> str:
        """路由到子图"""
        # 检查是否有智能路由的结果
        if hasattr(state, 'next_stage') and state.next_stage:
            return state.next_stage
        # 如果没有智能路由结果，根据当前阶段决定下一个子图
        return f"{state.stage.value}_graph"

    async def render_response(self, state: CoachState) -> Dict[str, Any]:
        """渲染响应"""
        # 检查是否有错误信息
        if hasattr(state, 'error') and state.error:
            return {
                "phase_status": "错误",
                "user_input": state.user_input,
                "transition_reason": "路由失败",
                "response": {
                    "content": state.message if hasattr(state, 'message') else state.error,
                    "buttons": []
                }
            }
        
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
