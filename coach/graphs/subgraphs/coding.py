from coach.graphs.base import SubGraph
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from typing import Dict, Any

class CodingSubGraph(SubGraph):
    """
    编码阶段子图
    """
    
    def __init__(self):
        super().__init__("coding")
    
    def build(self) -> StateGraph:
        """
        构建编码阶段子图
        """
        graph = StateGraph(CoachState)
        
        # 添加节点
        graph.add_node("validate_code", self.validate_code)
        graph.add_node("generate_feedback", self.generate_feedback)
        
        # 设置入口点
        graph.set_entry_point("validate_code")
        
        # 添加边
        graph.add_edge("validate_code", "generate_feedback")
        graph.add_edge("generate_feedback", END)
        
        return graph
    
    def validate_code(self, state: CoachState) -> Dict[str, Any]:
        """
        验证代码
        """
        # 这里可以添加代码验证逻辑
        # 例如检查代码格式、语法等
        return state.model_dump()
    
    def generate_feedback(self, state: CoachState) -> Dict[str, Any]:
        """
        生成反馈
        """
        # 这里可以添加反馈生成逻辑
        # 例如根据代码质量生成相应的反馈
        return state.model_dump()

# 构建函数
def build_coding_subgraph() -> StateGraph:
    """
    构建编码阶段子图
    """
    subgraph = CodingSubGraph()
    return subgraph.compile()
