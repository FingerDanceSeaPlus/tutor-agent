import chainlit as cl
from coach.schemas import CoachState
from coach.handlers.phase_handler import PhaseHandler
from coach.handlers.error_handler import ErrorHandler
from coach.services import StateService
from typing import Dict, List, Callable

class ActionHandler:
    """
    动作处理器
    负责统一处理所有动作回调
    """
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.state_service = StateService()
        self._action_registry: Dict[str, Callable] = {}
    
    async def route_action(self, state: CoachState, action: cl.Action) -> CoachState:
        """
        根据当前阶段和action类型路由到对应处理函数
        """
        try:
            phase = state.phase
            
            handler = PhaseHandler(state)
            
            # 验证状态
            if not handler.validate_state():
                state.ui_message = "状态验证失败，请重新设置题目。"
                return state
            
            if phase == "need_problem":
                return await handler.handle_need_problem_actions(action)
            elif phase == "thinking":
                return await handler.handle_thinking_actions(action)
            elif phase == "coding":
                return await handler.handle_coding_actions(action)
            elif phase == "testing":
                return await handler.handle_testing_actions(action)
            elif phase == "reflecting":
                return await handler.handle_reflecting_actions(action)
            else:
                # 处理未识别的阶段
                state.ui_message = f"未知的阶段：{phase}"
                return state
        except Exception as e:
            print(f"Error in route_action: {e}")
            import traceback
            traceback.print_exc()
            
            # 错误处理
            return self.error_handler.handle_action_error(e, state)
    
    def register_action(self, action_name: str, callback: Callable):
        """
        注册动作回调
        """
        self._action_registry[action_name] = callback
    
    def get_action_callback(self, action_name: str) -> Callable:
        """
        获取动作回调
        """
        return self._action_registry.get(action_name)
    
    def get_all_actions(self) -> List[str]:
        """
        获取所有已注册的动作
        """
        return list(self._action_registry.keys())

# 创建全局动作处理器实例
action_handler = ActionHandler()
