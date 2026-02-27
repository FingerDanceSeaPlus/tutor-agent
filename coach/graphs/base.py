from langgraph.graph import StateGraph
from coach.schemas import CoachState
from typing import Dict, Any, Callable, Optional

class BaseGraph:
    """
    基础图类
    所有图和子图的基类
    """
    
    def __init__(self):
        self.graph = None
    
    def build(self) -> StateGraph:
        """
        构建图
        """
        raise NotImplementedError("Subclasses must implement build method")
    
    def compile(self):
        """
        编译图
        """
        if not self.graph:
            self.graph = self.build()
        return self.graph.compile()
    
    def get_graph(self):
        """
        获取图实例
        """
        if not self.graph:
            self.graph = self.build()
        return self.graph
    
    def determine_next_node(self, state: CoachState) -> str:
        """
        根据状态决定下一步执行的节点
        """
        raise NotImplementedError("Subclasses must implement determine_next_node method")
    
    def transition_state(self, state: CoachState, next_phase: str, reason: str) -> Dict[str, Any]:
        """
        处理状态转换
        """
        state.phase = next_phase
        state.phase_status = "idle"
        state.transition_reason = reason
        return state.model_dump()
    
    def validate_state(self, state: CoachState) -> bool:
        """
        验证状态的一致性
        """
        # 基本验证逻辑
        if not state.problem:
            return False
        return True

class SubGraph(BaseGraph):
    """
    子图类
    """
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def build(self) -> StateGraph:
        """
        构建子图
        """
        raise NotImplementedError("Subclasses must implement build method")
