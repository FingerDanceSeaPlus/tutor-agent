from coach.graphs.base import SubGraph
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from typing import Dict, Any

class ReflectingSubGraph(SubGraph):
    """
    复盘阶段子图
    """
    
    def __init__(self):
        super().__init__("reflecting")
    
    def build(self) -> StateGraph:
        """
        构建复盘阶段子图
        """
        graph = StateGraph(CoachState)
        
        # 添加节点
        graph.add_node("generate_summary", self.generate_summary)
        graph.add_node("provide_variant", self.provide_variant)
        
        # 设置入口点
        graph.set_entry_point("generate_summary")
        
        # 添加边
        graph.add_edge("generate_summary", "provide_variant")
        graph.add_edge("provide_variant", END)
        
        return graph
    
    def generate_summary(self, state: CoachState) -> Dict[str, Any]:
        """
        生成总结
        """
        # 这里可以添加总结生成逻辑
        # 例如总结解题过程、提取关键知识点等
        return state.model_dump()
    
    def provide_variant(self, state: CoachState) -> Dict[str, Any]:
        """
        提供变式题
        """
        # 这里可以添加变式题生成逻辑
        # 例如根据原题生成相关的变式题
        return state.model_dump()

# 构建函数
def build_reflecting_subgraph() -> StateGraph:
    """
    构建复盘阶段子图
    """
    subgraph = ReflectingSubGraph()
    return subgraph.compile()
