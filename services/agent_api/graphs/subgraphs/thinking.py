from langgraph.graph import StateGraph, END
from typing import Dict, Any
from ...schemas.state import CoachState, IdeaSpec
from ...schemas.stage import Stage
from ...services.llm_service import LLMService


class ThinkingSubGraph:
    """思路分析子图"""
    def __init__(self):
        self.name = "thinking"
        self.llm_service = LLMService()

    def build(self) -> StateGraph:
        """构建子图"""
        graph = StateGraph(CoachState)

        # 添加节点
        graph.add_node("analyze_idea", self.analyze_idea)
        graph.add_node("generate_guidance", self.generate_guidance)

        # 添加边
        graph.set_entry_point("analyze_idea")
        graph.add_edge("analyze_idea", "generate_guidance")
        graph.add_edge("generate_guidance", END)

        return graph

    async def analyze_idea(self, state: CoachState) -> Dict[str, Any]:
        """分析用户思路"""
        user_input = state.user_input or ""
        if not user_input:
            return {"idea": None}

        # 构建提示词
        prompt = f"请分析以下解题思路的正确性、缺失点和错误点：\n\n{user_input}"

        # 调用LLM
        response = await self.llm_service.generate(prompt)

        # 构建IdeaSpec
        idea = IdeaSpec(
            user_idea_raw=user_input,
            analysis=response,
            guidance="",
            key_invariants=None,
            complexity=None
        )

        return {"idea": idea}

    async def generate_guidance(self, state: CoachState) -> Dict[str, Any]:
        """生成引导信息"""
        idea = state.idea
        if not idea:
            return {"idea": None}

        # 根据hint_level生成不同级别的引导
        hint_level = state.hint_level
        if hint_level == "low":
            guidance_prompt = f"请对以下思路给出低级别提示，只指出错误方向和提示问题：\n\n{idea.user_idea_raw}"
        elif hint_level == "mid":
            guidance_prompt = f"请对以下思路给出中级别提示，指出可用的关键思路/不变量和半步推导：\n\n{idea.user_idea_raw}"
        else:  # high
            guidance_prompt = f"请对以下思路给出高级别提示，提供完整推导与伪代码：\n\n{idea.user_idea_raw}"

        # 调用LLM
        guidance = await self.llm_service.generate(guidance_prompt)

        idea.guidance = guidance
        return {"idea": idea}
