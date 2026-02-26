from coach.schemas import CoachState
from typing import Optional

class ErrorHandler:
    """
    错误处理器
    负责集中处理所有错误
    """
    
    def __init__(self):
        pass
    
    def handle_error(self, error: Exception, context: str, state: Optional[CoachState] = None) -> CoachState:
        """
        处理错误并更新状态
        """
        error_message = f"{context}时发生错误: {str(error)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        # 如果没有状态，创建一个新的状态
        if not state:
            from coach.services import StateService
            state_service = StateService()
            state = state_service.init_state()
        
        # 更新状态，添加错误信息
        state.ui_message = (
            "❌ 处理失败\n\n"
            f"错误信息：{str(error)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        
        return state
    
    def handle_validation_error(self, error: Exception, state: Optional[CoachState] = None) -> CoachState:
        """
        处理验证错误
        """
        return self.handle_error(error, "验证", state)
    
    def handle_graph_error(self, error: Exception, state: Optional[CoachState] = None) -> CoachState:
        """
        处理图执行错误
        """
        return self.handle_error(error, "图执行", state)
    
    def handle_action_error(self, error: Exception, state: Optional[CoachState] = None) -> CoachState:
        """
        处理动作执行错误
        """
        return self.handle_error(error, "动作执行", state)
