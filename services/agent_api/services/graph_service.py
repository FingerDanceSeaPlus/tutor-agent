from typing import Dict, Any, Optional
from schemas.state import CoachState
from schemas.stage import Stage
from services.trace_service import TraceService


class GraphService:
    """图服务"""
    def __init__(self):
        self.trace_service = TraceService()

    def update_state(self, state: CoachState, updates: Dict[str, Any]) -> CoachState:
        """更新状态"""
        # 更新状态
        for key, value in updates.items():
            setattr(state, key, value)
        return state

    def validate_state(self, state: CoachState) -> bool:
        """验证状态"""
        if state.stage == Stage.S1_PROBLEM:
            return state.problem is not None and state.problem.ready
        elif state.stage == Stage.S2_IDEA:
            return state.idea is not None
        elif state.stage == Stage.S3_CODE:
            return state.code is not None and state.run_report and state.run_report.ok
        elif state.stage == Stage.S4_TEST:
            return state.test_report is not None and state.test_report.passed
        return True

    def transition_state(self, state: CoachState, next_stage: Stage, reason: str) -> CoachState:
        """状态转换"""
        state.stage = next_stage
        state.transition_reason = reason
        return state

    def store_trace(self, state: CoachState):
        """存储trace"""
        if state.session_id:
            # 转换trace为可存储格式
            trace_dict = {
                "events": [event.model_dump() for event in state.trace.events],
                "hint_level": state.hint_level,
                "current_stage": state.stage.value
            }
            self.trace_service.store_trace(state.session_id, trace_dict)

    def get_trace(self, session_id: str) -> Dict[str, Any]:
        """获取trace"""
        return self.trace_service.get_trace(session_id)

    def list_sessions(self) -> list:
        """列出所有会话"""
        return self.trace_service.list_sessions()
