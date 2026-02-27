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
            # 检查并添加缺失的属性，确保向后兼容
            if not hasattr(state, 'phase_status'):
                state.phase_status = "idle"
            if not hasattr(state, 'user_input'):
                state.user_input = ""
            if not hasattr(state, 'transition_reason'):
                state.transition_reason = ""
            
            # 检查是否需要自动切换阶段
            if state.phase_status == "done":
                state = self.transition_to_next_phase(state)
            
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
    
    def transition_to_next_phase(self, state: CoachState) -> CoachState:
        """
        自动切换到下一个阶段
        """
        phase_order = ["need_problem", "thinking", "coding", "testing", "reflecting"]
        current_index = phase_order.index(state.phase) if state.phase in phase_order else -1
        
        if current_index < len(phase_order) - 1:
            next_phase = phase_order[current_index + 1]
            state.phase = next_phase
            state.phase_status = "idle"
            state.transition_reason = f"自动从{state.phase}阶段切换到{next_phase}阶段"
            
            # 根据下一阶段生成相应的提示信息
            if next_phase == "thinking":
                state.ui_message = "### 进入思路阶段\n\n请分析题目，思考解题思路。"
            elif next_phase == "coding":
                state.ui_message = "### 进入编码阶段\n\n请根据思路编写代码。"
            elif next_phase == "testing":
                state.ui_message = "### 进入测试阶段\n\n请运行测试，验证代码是否正确。"
            elif next_phase == "reflecting":
                state.ui_message = "### 进入复盘阶段\n\n请总结解题过程，分析问题和解决方案。"
        
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
