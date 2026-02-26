from coach.graphs.base import SubGraph
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from typing import Dict, Any

class TestingSubGraph(SubGraph):
    """
    测试阶段子图
    """
    
    def __init__(self):
        super().__init__("testing")
    
    def build(self) -> StateGraph:
        """
        构建测试阶段子图
        """
        graph = StateGraph(CoachState)
        
        # 添加节点
        graph.add_node("run_tests", self.run_tests)
        graph.add_node("analyze_results", self.analyze_results)
        
        # 设置入口点
        graph.set_entry_point("run_tests")
        
        # 添加边
        graph.add_edge("run_tests", "analyze_results")
        graph.add_edge("analyze_results", END)
        
        return graph
    
    def run_tests(self, state: CoachState) -> Dict[str, Any]:
        """
        运行测试
        """
        # 这里可以添加测试运行逻辑
        # 例如执行用户代码并验证结果
        return state.model_dump()
    
    def analyze_results(self, state: CoachState) -> Dict[str, Any]:
        """
        分析测试结果
        """
        # 这里可以添加结果分析逻辑
        # 例如判断测试是否通过，生成错误信息等
        return state.model_dump()

# 构建函数
def build_testing_subgraph() -> StateGraph:
    """
    构建测试阶段子图
    """
    subgraph = TestingSubGraph()
    return subgraph.compile()
