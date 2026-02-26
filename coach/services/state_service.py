from coach.schemas import CoachState, Problem
from typing import Dict, Any

class StateService:
    """
    状态管理服务
    负责应用状态的管理、更新和验证
    """
    
    def __init__(self):
        pass
    
    def init_state(self) -> CoachState:
        """
        初始化状态
        """
        # 初始无题：提示用户先设置
        p = Problem(
            source="custom",
            id="custom-001",
            title="(未设置题目)",
            statement="请先粘贴题目原文。",
            raw_text="",
            constraints="",
            examples="",
            testcases=[]
        )
        return CoachState(problem=p)
    
    def validate_state(self, state: CoachState) -> bool:
        """
        验证状态的有效性
        """
        try:
            # 验证题目信息
            if not state.problem:
                return False
            
            # 验证阶段信息
            valid_phases = ["need_problem", "thinking", "coding", "testing", "reflecting"]
            if state.phase not in valid_phases:
                return False
            
            # 验证提示策略
            if not state.hint_policy:
                return False
            
            return True
        except Exception:
            return False
    
    def update_state(self, state: CoachState, updates: Dict[str, Any]) -> CoachState:
        """
        更新状态
        """
        try:
            # 应用更新
            for key, value in updates.items():
                # 支持嵌套属性更新，如 "problem.title"
                if "." in key:
                    parts = key.split(".")
                    obj = getattr(state, parts[0])
                    setattr(obj, parts[1], value)
                else:
                    setattr(state, key, value)
            
            return state
        except Exception as e:
            print(f"Error updating state: {e}")
            return state
    
    def reset_state(self) -> CoachState:
        """
        重置状态到初始状态
        """
        return self.init_state()
    
    def has_problem(self, state: CoachState) -> bool:
        """
        检查是否有题目
        """
        title = (state.problem.title or "").strip()
        return title not in {"", "(未设置题目)"} and (state.problem.statement or "").strip() != ""
    
    def has_thoughts(self, state: CoachState) -> bool:
        """
        检查是否有思路
        """
        return bool((state.user_attempt.thoughts or "").strip())
    
    def has_code(self, state: CoachState) -> bool:
        """
        检查是否有代码
        """
        return bool((state.user_attempt.code or "").strip())
    
    def passed(self, state: CoachState) -> bool:
        """
        检查是否通过测试
        """
        try:
            return bool(state.evaluation.passed)
        except Exception:
            return False
