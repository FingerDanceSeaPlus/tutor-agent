from coach.schemas import CoachState
from coach.graph import build_graph
from typing import Dict, Any

class GraphService:
    """
    图处理服务
    负责图的构建和执行
    """
    
    def __init__(self):
        self.graph = build_graph()
    
    def run_graph(self, state: CoachState) -> CoachState:
        """
        运行图处理
        """
        try:
            # LangGraph 支持 dict；这里用 model_dump / model_validate 来回转换更稳
            out = self.graph.invoke(state.model_dump(), config={
                "recursion_limit": 25,
                "debug": True
            })
            return CoachState.model_validate(out)
        except Exception as e:
            print(f"Error running graph: {e}")
            import traceback
            traceback.print_exc()
            # 错误处理：保持状态不变，添加错误信息
            state.ui_message = (
                "❌ 处理失败\n\n"
                f"错误信息：{str(e)}\n\n"
                "请稍后重试，或检查你的输入是否正确。"
            )
            return state
    
    def get_graph(self):
        """
        获取图实例
        """
        return self.graph
    
    def rebuild_graph(self):
        """
        重新构建图
        """
        self.graph = build_graph()
        return self.graph
