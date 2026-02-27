from langgraph.graph import StateGraph, END
from typing import Dict, Any
from schemas.state import CoachState, ProblemSpec, CorrectionItem
from schemas.stage import Stage
from services.llm_service import LLMService


class ProblemExtractionSubGraph:
    """题目提取子图"""
    def __init__(self):
        self.name = "problem_extraction"
        self.llm_service = LLMService()

    def build(self) -> StateGraph:
        """构建子图"""
        graph = StateGraph(CoachState)

        # 添加节点
        graph.add_node("extract_problem", self.extract_problem)
        graph.add_node("validate_problem", self.validate_problem)
        graph.add_node("clarify_problem", self.clarify_problem)

        # 添加边
        graph.set_entry_point("extract_problem")
        graph.add_edge("extract_problem", "validate_problem")
        graph.add_conditional_edges(
            "validate_problem",
            self.should_clarify,
            {
                True: "clarify_problem",
                False: END
            }
        )
        graph.add_edge("clarify_problem", "extract_problem")

        return graph

    async def extract_problem(self, state: CoachState) -> Dict[str, Any]:
        """提取题目信息"""
        # 使用LLM提取题目信息
        user_input = state.user_input or ""
        if not user_input:
            return {"problem": None}

        # 构建提示词
        prompt = f"请从以下输入中提取题目的标题、描述、示例和约束条件：\n\n{user_input}"

        # 调用LLM
        response = await self.llm_service.generate(prompt)

        # 解析LLM响应，构建ProblemSpec
        # 这里简化处理，实际实现需要更复杂的解析逻辑
        problem = ProblemSpec(
            title="提取的标题",
            description="提取的描述",
            examples=[{"input": "示例输入", "output": "示例输出"}],
            constraints=["约束条件1", "约束条件2"],
            ready=False
        )

        return {"problem": problem}

    async def validate_problem(self, state: CoachState) -> Dict[str, Any]:
        """验证题目信息"""
        problem = state.problem
        if not problem:
            return {"problem": None}

        # 检查题目信息是否完整
        is_complete = all([
            problem.title,
            problem.description,
            problem.examples,
            problem.constraints
        ])

        problem.ready = is_complete
        return {"problem": problem}

    async def clarify_problem(self, state: CoachState) -> Dict[str, Any]:
        """澄清题目信息"""
        # 生成澄清问题
        content = "请补充以下信息："
        if not state.problem.title:
            content += "\n- 题目标题"
        if not state.problem.description:
            content += "\n- 题目描述"
        if not state.problem.examples:
            content += "\n- 示例输入输出"
        if not state.problem.constraints:
            content += "\n- 约束条件"

        return {
            "phase_status": "需要补充信息",
            "user_input": state.user_input,
            "transition_reason": "题目信息不完整",
            "response": {
                "content": content,
                "buttons": []
            }
        }

    def should_clarify(self, state: CoachState) -> bool:
        """判断是否需要澄清"""
        return not (state.problem and state.problem.ready)
