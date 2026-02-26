from typing import Dict, Type, List
from coach.graphs.base import SubGraph

class GraphRegistry:
    """
    图注册中心
    用于注册和管理所有子图
    """
    
    def __init__(self):
        self._subgraphs: Dict[str, SubGraph] = {}
    
    def register(self, name: str, subgraph: SubGraph):
        """
        注册子图
        """
        self._subgraphs[name] = subgraph
    
    def get(self, name: str) -> SubGraph:
        """
        获取子图
        """
        return self._subgraphs.get(name)
    
    def get_all(self) -> Dict[str, SubGraph]:
        """
        获取所有子图
        """
        return self._subgraphs
    
    def get_names(self) -> List[str]:
        """
        获取所有子图名称
        """
        return list(self._subgraphs.keys())
    
    def contains(self, name: str) -> bool:
        """
        检查子图是否存在
        """
        return name in self._subgraphs

# 创建全局图注册中心实例
graph_registry = GraphRegistry()
