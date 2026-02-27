from langgraph.graph import StateGraph, END
from typing import Dict, Any
from schemas.state import CoachState
from schemas.stage import Stage
from services.llm_service import LLMService


class ReflectingSubGraph:
    """复盘子图"""
    def __init__(self):
        self.name = "reflecting"
        self.llm_service = LLMService()

    def build(self) -> StateGraph:
        """构建子图"""
        graph = StateGraph(CoachState)

        # 添加节点
        graph.add_node("generate_summary", self.generate_summary)
        graph.add_node("identify_weaknesses", self.identify_weaknesses)
        graph.add_node("generate_recommendations", self.generate_recommendations)

        # 添加边
        graph.set_entry_point("generate_summary")
        graph.add_edge("generate_summary", "identify_weaknesses")
        graph.add_edge("identify_weaknesses", "generate_recommendations")
        graph.add_edge("generate_recommendations", END)

        return graph

    async def generate_summary(self, state: CoachState) -> Dict[str, Any]:
        """生成总结"""
        # 生成解题过程总结
        summary = "# 解题过程总结\n\n"

        if state.problem:
            summary += f"## 题目\n{state.problem.title}\n{state.problem.description}\n\n"

        if state.idea:
            summary += f"## 思路分析\n{state.idea.analysis}\n\n"

        if state.code:
            summary += f"## 代码\n```python\n{state.code.code_text}\n```\n\n"

        if state.test_report:
            summary += f"## 测试结果\n"
            summary += f"通过状态: {'通过' if state.test_report.passed else '未通过'}\n"
            summary += f"总执行时间: {state.test_report.total_time}秒\n"
            summary += f"内存使用: {state.test_report.memory_usage}MB\n\n"

        return {"summary": summary}

    async def identify_weaknesses(self, state: CoachState) -> Dict[str, Any]:
        """识别薄弱点"""
        # 识别用户的薄弱点
        # 这里简化处理，实际实现需要更复杂的分析逻辑
        weaknesses = []

        if state.test_report and not state.test_report.passed:
            weaknesses.append("代码实现存在问题，部分测试用例未通过")

        if not state.idea:
            weaknesses.append("缺乏清晰的解题思路分析")

        return {"weaknesses": weaknesses}

    async def generate_recommendations(self, state: CoachState) -> Dict[str, Any]:
        """生成建议"""
        # 生成改进建议
        recommendations = []

        weaknesses = getattr(state, "weaknesses", [])
        if weaknesses:
            recommendations.append("针对测试失败的用例，仔细分析失败原因并修复代码")
            recommendations.append("在编写代码前，先梳理清晰的解题思路")

        recommendations.append("多练习类似题型，提高解题能力")
        recommendations.append("学习更多算法和数据结构知识")

        # 生成完整的复盘报告
        summary = getattr(state, "summary", "")
        weaknesses_str = "\n".join([f"- {w}" for w in weaknesses]) if weaknesses else "无明显薄弱点"
        recommendations_str = "\n".join([f"- {r}" for r in recommendations])

        report = f"{summary}\n## 薄弱点\n{weaknesses_str}\n\n## 改进建议\n{recommendations_str}"

        return {
            "report": report,
            "transition_reason": "生成了完整的复盘报告"
        }
