from langgraph.graph import StateGraph, END
from typing import Dict, Any
from datetime import datetime
from ...schemas.state import CoachState, CodeSpec, RunReport
from ...schemas.stage import Stage
from ...services.runner_service import RunnerService


class CodingSubGraph:
    """编码子图"""
    def __init__(self):
        self.name = "coding"
        self.runner_service = RunnerService()

    def build(self) -> StateGraph:
        """构建子图"""
        graph = StateGraph(CoachState)

        # 添加节点
        graph.add_node("extract_code", self.extract_code)
        graph.add_node("format_check", self.format_check)
        graph.add_node("run_examples", self.run_examples)

        # 添加边
        graph.set_entry_point("extract_code")
        graph.add_edge("extract_code", "format_check")
        graph.add_edge("format_check", "run_examples")
        graph.add_edge("run_examples", END)

        return graph

    async def extract_code(self, state: CoachState) -> Dict[str, Any]:
        """提取代码"""
        user_input = state.user_input or ""
        if not user_input:
            return {"code": None}

        # 从用户输入中提取代码块
        # 这里简化处理，实际实现需要更复杂的解析逻辑
        code_text = user_input
        language = "python"  # 默认语言，实际实现需要检测

        # 构建CodeSpec
        code = CodeSpec(
            language=language,
            code_text=code_text,
            format_ok=False,
            entrypoint_detected=False
        )

        return {"code": code}

    async def format_check(self, state: CoachState) -> Dict[str, Any]:
        """格式检查"""
        code = state.code
        if not code:
            return {"code": None}

        # 检查代码格式和入口点
        # 这里简化处理，实际实现需要更复杂的检查逻辑
        code.format_ok = True
        code.entrypoint_detected = True

        return {"code": code}

    async def run_examples(self, state: CoachState) -> Dict[str, Any]:
        """运行示例"""
        code = state.code
        if not code or not code.format_ok:
            return {"run_report": None}

        # 获取题目示例
        examples = []
        if state.problem:
            examples = state.problem.examples

        # 运行示例
        # 这里简化处理，实际实现需要调用Runner服务
        try:
            output = "示例运行结果"
            run_report = RunReport(
                ok=True,
                output=output,
                error=None,
                execution_time=0.1
            )
        except Exception as e:
            run_report = RunReport(
                ok=False,
                output="",
                error=str(e),
                execution_time=None
            )

        return {"run_report": run_report}
