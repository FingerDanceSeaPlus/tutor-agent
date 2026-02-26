from coach.schemas import CoachState, Problem
from typing import Optional, List, Dict, Any

class ValidationTool:
    """
    验证工具
    用于验证用户输入和状态
    """
    
    def __init__(self):
        pass
    
    def validate_problem(self, problem: Problem) -> bool:
        """
        验证题目是否有效
        """
        try:
            return bool(
                problem.title and 
                problem.statement and 
                problem.raw_text
            )
        except Exception:
            return False
    
    def validate_state(self, state: CoachState) -> bool:
        """
        验证状态是否有效
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
    
    def validate_code(self, code: str) -> bool:
        """
        验证代码是否有效
        """
        try:
            # 检查代码是否包含 solve 函数
            if "def solve" not in code:
                return False
            
            # 检查代码是否包含正确的函数签名
            if "def solve(inp: str) -> str" not in code:
                return False
            
            return True
        except Exception:
            return False
    
    def validate_thoughts(self, thoughts: str) -> bool:
        """
        验证思路是否有效
        """
        try:
            # 检查思路是否为空
            if not thoughts or not thoughts.strip():
                return False
            
            # 检查思路长度是否合理
            if len(thoughts.strip()) < 50:
                return False
            
            return True
        except Exception:
            return False
    
    def validate_test_case(self, test_case: Dict[str, str]) -> bool:
        """
        验证测试用例是否有效
        """
        try:
            return bool(
                test_case.get("input") and 
                test_case.get("expected")
            )
        except Exception:
            return False
    
    def validate_test_cases(self, test_cases: List[Dict[str, str]]) -> bool:
        """
        验证测试用例列表是否有效
        """
        try:
            if not test_cases:
                return False
            
            for test_case in test_cases:
                if not self.validate_test_case(test_case):
                    return False
            
            return True
        except Exception:
            return False

# 创建全局验证工具实例
validation_tool = ValidationTool()
