from coach.graphs.base import SubGraph
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from typing import Dict, Any

class ThinkingSubGraph(SubGraph):
    """
    思路阶段子图
    """
    
    def __init__(self):
        super().__init__("thinking")
    
    def build(self) -> StateGraph:
        """
        构建思路阶段子图
        """
        graph = StateGraph(CoachState)
        
        # 添加节点
        graph.add_node("analyze_problem", self.analyze_problem)
        graph.add_node("generate_hints", self.generate_hints)
        
        # 设置入口点
        graph.set_entry_point("analyze_problem")
        
        # 添加边
        graph.add_edge("analyze_problem", "generate_hints")
        graph.add_edge("generate_hints", END)
        
        return graph
    
    def analyze_problem(self, state: CoachState) -> Dict[str, Any]:
        """
        分析问题
        """
        # 这里可以添加问题分析逻辑
        # 例如提取关键信息、识别问题类型等
        return state.model_dump()
    
    def generate_hints(self, state: CoachState) -> Dict[str, Any]:
        """
        生成提示
        """
        # 这里可以添加提示生成逻辑
        # 例如根据问题类型生成相应的思路提示
        return state.model_dump()

# 构建函数
def build_thinking_subgraph() -> StateGraph:
    """
    构建思路阶段子图
    """
    subgraph = ThinkingSubGraph()
    return subgraph.compile()
