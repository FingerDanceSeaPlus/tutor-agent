from langgraph.graph import StateGraph
from coach.schemas import CoachState
from typing import Dict, Any, Callable

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
